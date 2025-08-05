import psutil
import socket


def coletar_interfaces():
    stats = psutil.net_if_stats()
    addrs = psutil.net_if_addrs()
    interfaces = {}

    for nome, addr_list in addrs.items():
        ativo = stats[nome].isup if nome in stats else False
        ip = [a.address for a in addr_list if a.family == socket.AF_INET]  # IPv4
        interfaces[nome] = {"ativo": ativo, "ip": ip}

    return interfaces


def coletar_portas_abertas():
    conexoes = psutil.net_connections(kind="inet")
    portas = {"tcp": set(), "udp": set()}

    for c in conexoes:
        if c.laddr and c.status == psutil.CONN_LISTEN:
            if c.type == socket.SOCK_STREAM:
                portas["tcp"].add(c.laddr.port)
            elif c.type == socket.SOCK_DGRAM:
                portas["udp"].add(c.laddr.port)

    return portas

def coletar_dados():
    dados = {
        "cpu": psutil.cpu_count(),
        "memoria_ram_livre": psutil.virtual_memory().available,
        "espaco_disco_livre": psutil.disk_usage('/').free,
        "interfaces": coletar_interfaces(),
        "portas_abertas": coletar_portas_abertas(),
    }
    return dados
