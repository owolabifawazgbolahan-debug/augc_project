import argostranslate.package
import argostranslate.translate


print("Downloading available translation packages...")

packages = argostranslate.package.get_available_packages()

for package in packages:
    if package.from_code == "en" and package.to_code in {
        "fr",
        "es",
        "de",
        "it",
        "yo",
        "ar",
        "ha"
    }:
        print(f"Installing: {package.from_code} -> {package.to_code}")

        downloaded_package = package.download()
        argostranslate.package.install_from_path(
            downloaded_package
        )

print("\nInstallation complete.")