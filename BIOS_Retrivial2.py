import platform
import json

try:
    import wmi
except ImportError:
    print("This script requires the 'wmi' module. Install it with 'pip install wmi'")
    exit(1)


def get_bios_info(c):
    bios = c.Win32_BIOS()[0]
    return {
        "Manufacturer": bios.Manufacturer,
        "Version": bios.SMBIOSBIOSVersion,
        "ReleaseDate": bios.ReleaseDate
    }


def get_cpu_info(c):
    cpu = c.Win32_Processor()[0]
    return {
        "Name": cpu.Name,
        "Cores": cpu.NumberOfCores,
        "Threads": cpu.NumberOfLogicalProcessors,
        "MaxClockSpeed (MHz)": cpu.MaxClockSpeed
    }


def get_ram_info(c):
    ram_modules = c.Win32_PhysicalMemory()
    total_ram = sum(int(r.Capacity) for r in ram_modules) / (1024**3)  # GB
    return {
        "TotalRAM (GB)": round(total_ram, 2),
        "Modules": len(ram_modules)
    }


def get_disk_info(c):
    disks = []
    for d in c.Win32_DiskDrive():
        disks.append({
            "Model": d.Model,
            "Size (GB)": round(int(d.Size) / (1024**3), 2) if d.Size else "Unknown"
        })
    return disks


def get_os_info(c):
    os = c.Win32_OperatingSystem()[0]
    return {
        "Name": os.Caption,
        "Version": os.Version,
        "Architecture": os.OSArchitecture
    }


def check_bios_version(bios, latest_version="F.33"):
    if bios["Version"] == latest_version:
        return f" BIOS version {bios['Version']} is up to date"
    else:
        return f"Your BIOS version is {bios['Version']}, latest expected is {latest_version}"


def main():
    if platform.system() != "Windows":
        print("This script only works on Windows systems (requires WMI). If you are using macOS or Linux, please run this script on a Windows machine or look for platform-specific alternatives.")
        return

    try:
        c = wmi.WMI()
    except Exception as e:
        print(f"Failed to initialize WMI: {e}")
        return

    system_info = {
        "BIOS": get_bios_info(c),
        "CPU": get_cpu_info(c),
        "RAM": get_ram_info(c),
        "Disks": get_disk_info(c),
        "OperatingSystem": get_os_info(c),
    }

    # Print as JSON (pretty format)
    print(json.dumps(system_info, indent=4))

    # Run compliance checks
    print("\n--- Checks ---")
    bios_check_result = check_bios_version(system_info["BIOS"])
    print(bios_check_result)
    if "up to date" not in bios_check_result:
        print("If your BIOS is outdated, visit your motherboard or system manufacturer's website for instructions on updating your BIOS. Ensure you follow all safety precautions during the update process.")


if __name__ == "__main__":
    main()
