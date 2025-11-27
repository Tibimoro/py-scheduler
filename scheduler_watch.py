import argparse, math
from kubernetes import client, config, watch

def load_client(kubeconfig=None):
    if kubeconfig:
        config.load_kube_config(kubeconfig)
    else:
        config.load_incluster_config()
    return client.CoreV1Api()

def bind_pod(api, pod, node_name):
    target = client.V1ObjectReference(kind="Node", name=node_name)
    meta = client.V1ObjectMeta(name=pod.metadata.name)
    body = client.V1Binding(target=target, metadata=meta)
    api.create_namespaced_binding(pod.metadata.namespace, body)

def choose_node(api, pod):
    nodes = api.list_node().items
    pods = api.list_pod_for_all_namespaces().items
    min_cnt, pick = math.inf, nodes[0].metadata.name
    for n in nodes:
        cnt = sum(1 for p in pods if p.spec.node_name == n.metadata.name)
        if cnt < min_cnt:
            min_cnt, pick = cnt, n.metadata.name
    return pick

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--scheduler-name", default="my-scheduler")
    parser.add_argument("--kubeconfig", default=None)
    args = parser.parse_args()

    api = load_client(args.kubeconfig)
    print(f"[watch] scheduler starting... name={args.scheduler_name}")

    w = watch.Watch()
    for event in w.stream(api.list_pod_for_all_namespaces, _request_timeout=60):
        pod = event['object']
        if not pod or not hasattr(pod, 'spec'):
            continue
        if pod.spec.node_name or pod.spec.scheduler_name != args.scheduler_name:
            continue
        try:
            node = choose_node(api, pod)
            bind_pod(api, pod, node)
            print(f"Bound {pod.metadata.namespace}/{pod.metadata.name} -> {node}")
        except Exception as e:
            print("error:", e)

if __name__ == "__main__":
    main()
