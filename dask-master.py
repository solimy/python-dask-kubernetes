from datetime import datetime
from dask_kubernetes import KubeCluster
from dask.distributed import Client
from dask import compute, delayed
from dask.distributed import get_worker, LocalCluster
import os
import json
import psutil
import dask.dataframe as dd
import pandas as pd
import logging as logger

logger.basicConfig(
    format='%(asctime)s %(process)-5d %(levelname)-8s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    level=os.getenv("LOGLEVEL","INFO")
)
LOCAL = json.loads(os.getenv('LOCAL', 'false'))
CLUSTER = None


def main():
    logger.info('-:- MAIN -:-')
    try:
        data = fetch_data()
        data = transform_data(data)
        save_data(data)
    except:
        logger.critical('', exc_info=True) 
        logger.critical('-:- MAIN : KO -:-')
        exit(1)
    logger.info('-:- MAIN : Done -:-')


def fetch_data():
    logger.info('-:- Fetching data -:-')
    data = pd.DataFrame.from_records([{"index": i} for i in range(1000000)], index="index")
    logger.info('-:- Fetching data : Done -:-')
    return data


def transform_data(data):
    logger.info('-:- Transforming data -:-')
    client = Client(CLUSTER)
    ddf = dd.from_pandas(data, 10000)
    logger.info('Building DAG...')
    delayed_results = [
        delayed(test)(ddf.get_partition(partition))
        for partition
        in range(ddf.npartitions)
    ]
    logger.info('Building DAG... Done.')
    logger.info('Computing results...')
    results = compute(*delayed_results)
    logger.info('Computing results... Done.')
    logger.info('Concatenating results...')
    data = pd.concat([*results])
    logger.info('Concatenating results... Done.')
    client.close()
    logger.info('-:- Transforming data : Done -:-')
    return data


def test(data):
    worker = get_worker()
    data["worker.ip"] = worker.ip
    data["worker.id"] = worker.id
    data["worker.thread_id"] = worker.thread_id
    data["cpu.percent"] = psutil.cpu_percent()
    data["mem.percent"] = psutil.virtual_memory().percent
    logger.info(f'worker.ip:{worker.ip}|worker.id:{worker.id}|worker.thread_id:{worker.thread_id}')
    return data


def save_data(data):
    logger.info('-:- Saving data -:-')
    now = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
    data.to_csv(f'{now}_data.csv')
    workers = [*(data['worker.ip'] + " -:- " + data['worker.id']).unique()]
    json.dump(workers, open(f'{now}_workers.json', 'w'), indent=4)
    logger.info('-:- Saving data : Done -:-')


if __name__ == "__main__":
    if LOCAL:
        cluster = LocalCluster()
        logger.info('CLUSTER="LOCAL"')
    else:
        cluster = KubeCluster.from_yaml('dask-worker.yaml')
        cluster.adapt(minimum=5, maximum=20)
        logger.info('CLUSTER="KUBERNETES"')
    CLUSTER = cluster
    main()
    cluster.close()
