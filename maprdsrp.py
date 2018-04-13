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
print("\n Please enter the login information for your cluster user (ex. 'mapr')")
user=input("\nUsername: ")
passwd = getpass.getpass()
print("\n Here are the environments available to you today:")
print("1. MapR Data Science Refinery with Apache Zeppeline")
print("2. MapR Data Science Refinery with R Studio & Shiny")
print("3. MapR Data Science Refinery with Tensorflow")
print("4. MapR Data Science Refinery Base Image (Centos7)")
containerenv = input("\n Which one would you like to launch? ")
print("\nThank You!")
pyVersion = input("\n Do you want Python 2 or Python 3? ")
print("\nThank You!")
libEnv = input("\n Do you want us to install any Python libraries? (Possible values are MatPlotLib, SciKitLearn, NumPy, SciPy, Pandas): ")
print("\nThank You!")
print ("\nBuilding Your MapR Data Science Refinery...\n")

# Generate ticket and export to Base64
cmd = "echo '" + passwd + "' | /opt/mapr/bin/maprlogin password"
ps = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
output = ps.communicate()[0]
#print (output)
file = open("/tmp/maprticket_5000","r")
ticket = file.read()
ticket64 = str(base64.b64encode(bytes(ticket.strip(),'utf-8')), 'utf-8')
file.close()
##print(ticket64)


## Set image and parameters based on menu selection

# Cluster Config
MAPR_CLUSTER = "my.cluster.com" 
MAPR_CLDB_HOSTS = "<>"
HOST_IP = "<>"
MAPR_CONTAINER_USER = user
MAPR_CONTAINER_PASSWORD = passwd
ZEPPELIN_ARCHIVE_PYTHON = "/mapr/my.cluster.com/user/mapr/python_envs/python_3_numpy.zip"
    
# Kubernetes config
namespace = 'demo-ns'
config.load_kube_config()
v1 = client.CoreV1Api()
v1apps = client.AppsV1Api()
api_version = 'v1'

# Set image and parameters based on menu selection
if containerenv == '1':
    metadata_d = {"name": "dsrpod","namespace": namespace,"labels": {"app": "dsrdemo"}}
    spec_d = {"selector": {"matchLabels": {"app": "dsrdemo"}},"template": {"metadata": {"labels": {"app": "dsrdemo"}},"spec": {"containers": [{"image": "maprtech/data-science-refinery:latest","imagePullPolicy": "Always","name": "dsrdemo","args": ["sleep","1000000"],"env": [{"name": "MAPR_CLUSTER","value": MAPR_CLUSTER},{"name": "MAPR_CLDB_HOSTS","value": MAPR_CLDB_HOSTS},{"name": "MAPR_CONTAINER_USER","value": MAPR_CONTAINER_USER},{"name": "MAPR_CONTAINER_GROUP","value": "mapr"},{"name": "ZEPPELIN_NOTEBOOK_DIR","value": "/mapr/zeppelin/shared-notebooks"},{"name": "MAPR_CONTAINER_PASSWORD","value": MAPR_CONTAINER_PASSWORD},{"name": "MAPR_TICKETFILE_LOCATION","value": "/tmp/mapr_ticket/CONTAINER_TICKET"},{"name": "ZEPPELIN_ARCHIVE_PYTHON","value": ZEPPELIN_ARCHIVE_PYTHON},{"name": "HOST_IP","value": HOST_IP},{"name": "DEPLOY_MODE","value": "kubernetes"}],"ports": [{"containerPort": 9995,"name": "zeppelin"}],"volumeMounts": [{"name": "maprvolume","mountPath": "/mapr"},{"name": "maprticket","mountPath": "/tmp/mapr_ticket"}]}],"volumes": [{"name": "maprvolume","persistentVolumeClaim": {"claimName": "demopvc"}},{"name": "maprticket","secret": {"secretName": "demosecret"}}]}}} 
elif containerenv == '2':
    metadata_d = {"name": "rpod","namespace": namespace,"labels": {"app": "dsrdemo"}}
    spec_d = {"selector": {"matchLabels": {"app": "dsrdemo"}},"template": {"metadata": {"labels": {"app": "dsrdemo"}},"spec": {"containers": [{"image": "rsilvery/dsr-labs:rstudio_zeppelin","imagePullPolicy": "Never","name": "dsrdemo","args": ["sleep","1000000"],"env": [{"name": "MAPR_CLUSTER","value": MAPR_CLUSTER},{"name": "MAPR_CLDB_HOSTS","value": MAPR_CLDB_HOSTS},{"name": "MAPR_CONTAINER_USER","value": MAPR_CONTAINER_USER},{"name": "MAPR_CONTAINER_GROUP","value": "mapr"},{"name": "MAPR_CONTAINER_PASSWORD","value": MAPR_CONTAINER_PASSWORD},{"name": "MAPR_TICKETFILE_LOCATION","value": "/tmp/mapr_ticket/CONTAINER_TICKET"},{"name": "HOST_IP","value": HOST_IP},{"name": "DEPLOY_MODE","value": "kubernetes"}],"ports": [{"containerPort": 8787,"name": "zeppelin"}],"volumeMounts": [{"name": "maprvolume","mountPath": "/mapr"},{"name": "maprticket","mountPath": "/tmp/mapr_ticket"}]}],"volumes": [{"name": "maprvolume","persistentVolumeClaim": {"claimName": "demopvc"}},{"name": "maprticket","secret": {"secretName": "demosecret"}}]}}}
elif containerenv == '3':
    metadata_d = {"name": "tfpod","namespace": namespace,"labels": {"app": "dsrdemo"}}
    spec_d = {"selector": {"matchLabels": {"app": "dsrdemo"}},"template": {"metadata": {"labels": {"app": "dsrdemo"}},"spec": {"containers": [{"image": "rsilvery/dsr-labs:tf_zeppelin","imagePullPolicy": "Never","name": "dsrdemo","args": ["sleep","1000000"],"env": [{"name": "MAPR_CLUSTER","value": MAPR_CLUSTER},{"name": "MAPR_CLDB_HOSTS","value": MAPR_CLDB_HOSTS},{"name": "MAPR_CONTAINER_USER","value": MAPR_CONTAINER_USER},{"name": "MAPR_CONTAINER_GROUP","value": "mapr"},{"name": "MAPR_CONTAINER_PASSWORD","value": MAPR_CONTAINER_PASSWORD},{"name": "MAPR_TICKETFILE_LOCATION","value": "/tmp/mapr_ticket/CONTAINER_TICKET"},{"name": "HOST_IP","value": HOST_IP},{"name": "DEPLOY_MODE","value": "kubernetes"}],"ports": [{"containerPort": 6006,"name": "zeppelin"}],"volumeMounts": [{"name": "maprvolume","mountPath": "/mapr"},{"name": "maprticket","mountPath": "/tmp/mapr_ticket"}]}],"volumes": [{"name": "maprvolume","persistentVolumeClaim": {"claimName": "demopvc"}},{"name": "maprticket","secret": {"secretName": "demosecret"}}]}}}
elif containerenv == '4':
    metadata_d = {"name": "basepod","namespace": namespace,"labels": {"app": "dsrdemo"}} 
    spec_d = {}

# Create secret in Kubernetes
#kind = 'Secret'
#metadata = {'name': 'demosecret', 'namespace': namespace}
#data = {'CONTAINER_TICKET': ticket64}
#body = kubernetes.client.V1Secret(api_version, data, kind, metadata, type='Opaque' )
#api_response = v1.create_namespaced_secret(namespace, body)
#
# create persistent volume claim 
#kind = 'PersistentVolume'
#metadata = {'name': 'demopv', 'namespace': namespace}
#spec = {"capacity": {"storage": "5Gi"},"accessModes": ["ReadWriteOnce"],"claimRef": {"namespace": namespace,"name": "demopvc"},"flexVolume": {"driver": "mapr.com/maprfs","options": {"platinum": "false","cluster": MAPR_CLUSTER,"cldbHosts": MAPR_CLDB_HOSTS,"volumePath": "/user/mapr","securityType": "secure","ticketSecretName": "demosecret","ticketSecretNamespace": namespace}}} 
#body = kubernetes.client.V1PersistentVolume(api_version, kind, metadata, spec)
#api_response = v1.create_persistent_volume(body)
#
## create persistent volume claim 
#kind = 'PersistentVolumeClaim'
#metadata = {'name': 'demopvc', 'namespace': namespace}
#spec = {"accessModes":["ReadWriteOnce"],"resources":{"requests":{"storage":"5G"}}}
#body = kubernetes.client.V1PersistentVolumeClaim(api_version, kind, metadata, spec)
#api_response = v1.create_namespaced_persistent_volume_claim(namespace, body)
#
### create service
#kind = 'Service'
#metadata = {"name": "dsrsevice2","namespace": namespace,"labels": {"run": "dsrdemo"}}
#spec = {"ports": [{"port": 9995,"protocol": "TCP","name": "zeppelin"}],"externalIPs": [HOST_IP],"selector": {"app": "dsrdemo"}}
#body = kubernetes.client.V1Service(api_version, kind, metadata, spec)
#api_response = v1.create_namespaced_service(namespace, body)
##
# create Deployment
api_version_d = 'apps/v1' 
kind = 'Deployment'
body = kubernetes.client.V1Deployment(api_version_d, kind, metadata_d, spec_d)
api_response = v1apps.create_namespaced_deployment(namespace, body)
