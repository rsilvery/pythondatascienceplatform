import getpass
import subprocess
import base64
import time
import kubernetes
from kubernetes import client, config
from kubernetes.client.rest import ApiException

## Pick image
print("**********************************************************")
print("\nHi! Welcome to the MapR Data Science Refinery Platform!")
print("\n Here are the environments available to you today:")
print("1. MapR Data Science Refinery with Apache Zeppeline")
print("2. MapR Data Science Refinery with R Studio & Shiny")
print("3. MapR Data Science Refinery with Tensorflow")
print("4. MapR Data Science Refinery Base Image (Centos7)")
containerenv = input("\n Which one would you like to launch? ")
print("Thank You!")
print("\n Is there a Python environment you'd like to use?")
pythonenv = input("Path to Python archive in MapR-FS: ex. /user/mapr/my_python_env.zip\n")
print("Thank You!")
print("\n Please enter the login information for your cluster user (ex. 'mapr')")
user=input("Username: ")
passwd = getpass.getpass()
##print(user,passwd)

# Generate ticket and export to Base64
cmd = "echo '" + passwd + "' | /opt/mapr/bin/maprlogin password"
ps = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
output = ps.communicate()[0]
#print (output)
file = open("/tmp/maprticket_5000","r")
ticket = file.read()
ticket64 = str(base64.b64encode(bytes(ticket.strip(),'utf-8')), 'utf-8')
file.close()
#print(ticket64)

# Set image and parameters based on menu selection

# Cluster Config
MAPR_CLUSTER = "my.cluster.com" 
MAPR_CLDB_HOSTS = "172.24.10.185 172.24.8.64 172.24.11.94"
HOST_IP = "172.24.11.213"
MAPR_CONTAINER_USER = user
MAPR_CONTAINER_PASSWORD = passwd
#ZEPPELIN_ARCHIVE_PYTHON = pythonenv
	
# Kubernetes config
namespace = 'demo-ns'
config.load_kube_config()
v1 = client.CoreV1Api()
api_version = 'v1'

# Set image and parameters based on menu selection
if containerenv == '1':
    print("\n Where would you like to store your Zeppelin notebooks??")
    notebookpath = input("Path to directory in MapR-FS: ex. /user/mapr/notebooks\n")
    ZEPPELIN_NOTEBOOK_DIR = notebookpath
    print ("Building MapR Data Science Refinery with Apache Zeppelin")
    podmetadata = {'name': 'dsrpod', 'namespace': namespace}
    podspec = {"containers": [{"name": "dsrcontainer","imagePullPolicy": "Always","image": "maprtech/data-science-refinery:latest","args": ["sleep","1000000"],"resources": {"requests": {"memory": "2Gi","cpu": "500m"}},"env": [{"name": "MAPR_CLUSTER","value": MAPR_CLUSTER},{"name": "MAPR_CLDB_HOSTS","value": MAPR_CLDB_HOSTS},{"name": "MAPR_CONTAINER_USER","value": MAPR_CONTAINER_USER},{"name": "MAPR_CONTAINER_GROUP","value": "mapr"},{"name": "ZEPPELIN_NOTEBOOK_DIR","value": ZEPPELIN_NOTEBOOK_DIR},{"name": "MAPR_CONTAINER_PASSWORD","value": MAPR_CONTAINER_PASSWORD},{"name": "MAPR_TICKETFILE_LOCATION","value": "/tmp/mapr_ticket/CONTAINER_TICKET"},{"name": "HOST_IP","value": "172.24.11.213"},{"name": "DEPLOY_MODE","value": "kubernetes"}],"volumeMounts": [{"mountPath": "/mapr","name": "maprk8svolume"},{"mountPath": "/tmp/mapr_ticket","name": "maprticket"}]}],"volumes": [{"name": "maprk8svolume","persistentVolumeClaim": {"claimName": "demopvc"}},{"name": "maprticket","secret": {"secretName": "demosecret"}}]}
elif containerenv == '4':
    print ("Building MapR Data Science Refinery Base Image (Centos7)")
    podmetadata = {'name': 'centospod', 'namespace': namespace}
    podspec = {"containers":[{"name":"centoscontainer","imagePullPolicy":"Always","image":"centos:centos7","args":["sleep","1000000"],"resources":{"requests":{"memory":"2Gi","cpu":"500m"}},"volumeMounts":[{"mountPath":"/mapr","name":"maprvolume"}]}],"volumes":[{"name":"maprvolume","persistentVolumeClaim":{"claimName":"demopvc"}}]}

# Create secret in Kubernetes
kind = 'Secret'
metadata = {'name': 'demosecret', 'namespace': namespace}
data = {'CONTAINER_TICKET': ticket64}
body = kubernetes.client.V1Secret(api_version, data, kind, metadata, type='Opaque' )
api_response = v1.create_namespaced_secret(namespace, body)

# create persistent volume claim 
kind = 'PersistentVolume'
metadata = {'name': 'demopv', 'namespace': namespace}
spec = {"capacity": {"storage": "5Gi"},"accessModes": ["ReadWriteOnce"],"claimRef": {"namespace": namespace,"name": "demopvc"},"flexVolume": {"driver": "mapr.com/maprfs","options": {"platinum": "false","cluster": MAPR_CLUSTER,"cldbHosts": MAPR_CLDB_HOSTS,"volumePath": "/user/mapr","securityType": "secure","ticketSecretName": "demosecret","ticketSecretNamespace": namespace}}} 
body = kubernetes.client.V1PersistentVolume(api_version, kind, metadata, spec)
api_response = v1.create_persistent_volume(body)

# create persistent volume claim 
kind = 'PersistentVolumeClaim'
metadata = {'name': 'demopvc', 'namespace': namespace}
spec = {"accessModes":["ReadWriteOnce"],"resources":{"requests":{"storage":"5G"}}}
body = kubernetes.client.V1PersistentVolumeClaim(api_version, kind, metadata, spec)
api_response = v1.create_namespaced_persistent_volume_claim(namespace, body)

# create pod 
kind = 'Pod'
body = kubernetes.client.V1Pod(api_version, kind, podmetadata, podspec)
api_response = v1.create_namespaced_pod(namespace, body) 
