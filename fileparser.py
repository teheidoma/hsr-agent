from winregistry import WinRegistry
class FileParser:
    REGISTRY_PATH = 'HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\Star Rail'

    def getPath(self):
        with WinRegistry() as reg:
            value = reg.read_entry(self.REGISTRY_PATH, 'InstallPath').value
            return value + '\\Games\\StarRail_Data\\webCaches\\2.14.0.0\\Cache\\Cache_Data\\data_2'

