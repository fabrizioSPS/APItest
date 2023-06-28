import subprocess

def sum_of_numbers(a, b):
    # Execute the C application
    result = subprocess.run(['./InternalCode/Application/ConsoleApplication.exe', f"{a}", f"{b}"], capture_output=True, text=True)

    # Extract and return the output
    output = result.stdout.strip()
    return int(output)
