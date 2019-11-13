# python-dask-kubernetes
Dask kubernetes deployment exemple
**WIP - Poor content atm. - need rework/testing.**
**This is an experiementation project.**


## SETUP
- ````kubectl apply -f dask-nsp.yaml````
	> Create a "dask" namespace.
- ````kubectl apply -f dask-master-sa.yaml````
	> Create a service account for the dask "master" to manage pods.
- ````kubectl apply -f dask-master-rb.yaml````
	> Create a role binding with the necessary roles for pods management.
- ````kubectl apply -f dask-master.yaml````
	> Create the "master" deployment named "python" we will attach to.
- ````kubectl -n dask get pods````
	> List all pods.
- Copy the "pod/python-...." pod name without the "pod/" part.
	> eg: "python-6b77cf9894-n2s4k"
- ````kubectl -n dask exec -it THE_POD_NAME bash````
	> Where THE_POD_NAME is what you copied the step before.

You are now inside the pod.
- ````pip install pyvim````
	> Text editor to add/edit code files.
- Copy/paste files :
	- requirements.txt
	- dask-master.py
	- dask-worker.yaml
	> Eg with pyvim :
		*Copy* the requirements.txt content,
		````pyvim requirements.txt````,
		*paste*,
		````:wq````.
- ````pip install -r requirements.txt````

Setup is done !
		


## RUN

````python dask-master.py; export CODE=$?; echo $(date +%Y-%m-%d\ %H:%M:%S) $CODE````

## KNOWN ISSUES
- exits with error code 137.
- exits with error code 1.
and :
 ````distributed.scheduler.KilledWorker: ("('from_pandas-AN_UUID', 2000)", <Worker 'tcp://AN_IP:A_PORT', memory: 0, processing: 9999>)````
	> eg: from_pandas-AN_UUID -> 'from_pandas-b823d0872c18ebc1510e9e03b3ccf52a'