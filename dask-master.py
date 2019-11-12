from datetime import datetime
from dask_kubernetes import KubeCluster
from dask.distributed import Client
from dask import compute, delayed
from dask.distributed import get_worker, LocalCluster
import os
import json
import dask.dataframe as dd
import pandas as pd


LOCAL = json.loads(os.getenv('LOCAL', 'false'))
CLUSTER = None


def main():
    print('-:- MAIN -:-')
    data = fetch_data()
    data = transform_data(data)
    save_data(data)
    print('-:- MAIN : Done -:-')


def fetch_data():
    print('-:- Fetching data -:-')
    data = pd.DataFrame.from_records([{"index": i} for i in range(1000)], index="index")
    print('-:- Fetching data : Done -:-')
    return data


def transform_data(data):
    print('-:- Transforming data -:-')
    client = Client(CLUSTER)
    ddf = dd.from_pandas(data, 1000)
    print('Building DAG...')
    delayed_results = [
        delayed(test)(ddf.get_partition(partition))
        for partition
        in range(ddf.npartitions)
    ]
    print('Building DAG... Done.')
    print('Computing results...')
    results = compute(*delayed_results)
    print('Computing results... Done.')
    print('Concatenating results...')
    data = pd.concat([*results])
    print('Concatenating results... Done.')
    client.close()
    print('-:- Transforming data : Done -:-')
    return data


def test(data):
    worker = get_worker()
    data["worker.ip"] = worker.ip
    data["worker.id"] = worker.id
    data["worker.thread_id"] = worker.thread_id
    print(f'worker.ip:{worker.ip}|worker.id:{worker.id}|worker.thread_id:{worker.thread_id}')
    return data


def save_data(data):
    print('-:- Saving data -:-')
    data.to_csv(f'{datetime.now().strftime("%Y-%m-%d_%H:%M:%S")}_data.csv')
    print('-:- Saving data : Done -:-')


if __name__ == "__main__":
    if LOCAL:
        cluster = LocalCluster()
        print('CLUSTER="LOCAL"')
    else:
        cluster = KubeCluster.from_yaml('dask-worker.yaml')
        cluster.adapt(minimum=0, maximum=20)
        print('CLUSTER="KUBERNETES"')
    CLUSTER = cluster
    main()
    cluster.close()
