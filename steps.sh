# create a custom python image
# docker build -t my-python-image:latest .
# load it to minikube
# minikube image load my-python-image:latest
# delete namespace in case it was there before
kubectl delete namespace argo

kubectl apply -f namespace.yaml
# install ARGO server
kubectl apply -n argo -f https://github.com/argoproj/argo-workflows/releases/download/v3.2.4/install.yaml

# echo -n "your-copernicus-token" | base64
# echo -n "your-copernicus-secret" | base64

kubectl apply -f secrets.yaml

# kubectl apply -f pv.yaml

kubectl create configmap scripts --from-file=dummy.py --from-file=download.py -n argo

# need more explanation
kubectl apply -f rbac_argo.yaml -n argo
kubectl apply -f pvc.yaml

kubectl apply -f workflow_argo.yaml -n argo

# DEBUG 
echo "PODS"
kubectl get pods -n argo

echo "WF"
kubectl get wf -n argo

echo "PV"
kubectl get pv -n argo

echo "PVC"
kubectl get pvc -n argo
echo ""
echo "After finishing the script make sure PV and PVC are bounded, in case they are not! apply the pv.yaml file again"

