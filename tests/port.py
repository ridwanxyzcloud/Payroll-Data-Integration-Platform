import socket


def test_connection(host, port):
    try:
        with socket.create_connection((host, port), timeout=10) as sock:
            print(f"Connection to {host} on port {port} succeeded")
    except Exception as e:
        print(f"Connection to {host} on port {port} failed: {str(e)}")

if __name__ == '__main__':
    test_connection('payroll-workgroup.637423632863.eu-west-2.redshift-serverless.amazonaws.com', 5439)