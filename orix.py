import os
import subprocess
import sys
import logging
from typing import List, Generator, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Constants
PIPAL_REPO = "https://github.com/digininja/pipal.git"
PIPAL_DIR = "./pipal"
SECLISTS_LOCAL_DIR = "/usr/share/wordlists/seclists/Passwords/"

# Check for distro module and install if not detected
try:
    import distro
except ImportError:
    logging.info("The 'distro' module is not installed. Installing it now...")
    subprocess.run([sys.executable, "-m", "pip", "install", "distro"], check=True)
    import distro


def run_command(command: List[str]) -> None:
    """Run a shell command and handle errors."""
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        logging.error(f"Error executing command: {' '.join(command)}\n{e}")
        sys.exit(1)


def install_package(package_manager: str, package_name: str) -> None:
    """Install a package using the specified package manager."""
    if package_manager == "pacman":
        run_command(["sudo", "pacman", "-S", "--noconfirm", package_name])
    elif package_manager == "apt-get":
        run_command(["sudo", "apt-get", "install", "-y", package_name])
    elif package_manager == "dnf":
        run_command(["sudo", "dnf", "install", "-y", package_name])
    else:
        logging.error(f"Unsupported package manager: {package_manager}")
        sys.exit(1)


def detect_distro() -> str:
    """Detect the Linux distribution and return the name."""
    distro_name = distro.id().lower()
    if distro_name in ["debian", "ubuntu"]:
        return "debian/ubuntu"
    elif distro_name == "fedora":
        return "fedora"
    elif distro_name == "arch":
        return "arch"
    else:
        return "unknown"


def setup_pipal(distro_name: str) -> None:
    """Setup Pipal repository and install Ruby."""
    if not os.path.exists(PIPAL_DIR):
        logging.info(f"Cloning Pipal repository from {PIPAL_REPO}...")
        run_command(["git", "clone", PIPAL_REPO, PIPAL_DIR])
    else:
        logging.info("Pipal directory already exists. Skipping cloning.")

    logging.info("Ensuring Ruby is installed...")
    if distro_name == "arch":
        install_package("pacman", "ruby")
    elif distro_name == "debian/ubuntu":
        install_package("apt-get", "ruby")
    elif distro_name == "fedora":
        install_package("dnf", "ruby")
    logging.info("Ruby installed.")


def install_dependencies() -> None:
    """Install Pipal dependencies and optionally install CeWL for different Linux distros."""
    distro_name = detect_distro()
    logging.info(f"Detected distribution: {distro_name}")

    if distro_name not in ["arch", "debian/ubuntu", "fedora"]:
        logging.error("Unknown distribution. Unable to install dependencies automatically.")
        return

    setup_pipal_input = get_yes_no_input("Do you want to download and setup Pipal dependencies? (yes/no): ")
    if setup_pipal_input:
        setup_pipal(distro_name)

    install_cewl_input = get_yes_no_input("Do you want to install/update CeWL? (yes/no): ")
    if install_cewl_input:
        if distro_name == "arch":
            install_package("pacman", "cewl")
        elif distro_name == "debian/ubuntu":
            install_package("apt-get", "cewl")
        elif distro_name == "fedora":
            install_package("dnf", "cewl")
        logging.info("CeWL installed.")


def get_yes_no_input(prompt: str) -> bool:
    """Get a yes/no input from the user."""
    while True:
        response = input(prompt).strip().lower()
        if response in {'yes', 'y'}:
            return True
        elif response in {'no', 'n'}:
            return False
        logging.warning("Invalid input. Please enter 'yes' or 'no'.")


def read_patterns(pattern_file: str) -> Generator[str, None, None]:
    """Read patterns from the given file and return as a generator."""
    try:
        with open(pattern_file, 'r') as f:
            for line in f:
                if line.strip():
                    yield line.strip()
    except FileNotFoundError:
        logging.error(f"Error: The file {pattern_file} does not exist.")
        sys.exit(1)
    except Exception as e:
        logging.error(f"An error occurred while reading {pattern_file}: {e}")
        sys.exit(1)


def leet_speak_variants(word: str) -> set:
    """Generate leet speak variants for a given word."""
    replacements = {'a': '@', 'e': '3', 'i': '1', 'o': '0', 's': '$'}
    variants = {word}
    for char, replacement in replacements.items():
        if char in word:
            variants.add(word.replace(char, replacement))
    return variants


def generate_password_variants(words: List[str], patterns: List[str]) -> List[str]:
    """Generate password-like variants for each word using the patterns."""
    variants = set(words)
    years = ['2023', '2024']
    special_chars = ['!', '@', '#', '$', '%']
    number_sequences = ['123', '1234', '12345']

    for word in words:
        variants.update(leet_speak_variants(word))
        for pattern in patterns:
            variants.add(word + pattern)
            variants.add(pattern + word)
        for item in years + special_chars + number_sequences:
            variants.add(word + item)
            variants.add(item + word)
        variants.add(word + word)  # Duplicated word
        variants.add(word[::-1])  # Full reverse
        if len(word) > 1:
            mid = len(word) // 2
            variants.add(word[:mid][::-1] + word[mid:])  # Reverse first half
            variants.add(word[:mid] + word[mid:][::-1])  # Reverse second half
        variants.add(word.capitalize())  # Capitalize first letter
        if len(word) > 1:
            variants.add(word[0].upper() + word[1:])  # Camel case

    return list(variants)


def cewl_crawl() -> Optional[str]:
    """Prompt user for CeWL options and perform web crawling."""
    use_cewl = get_yes_no_input("Would you like to use CeWL to crawl a website for passwords? (yes/no): ")
    if not use_cewl:
        return None

    url = input("Enter the URL to crawl: ").strip()
    depth = input("Enter crawl depth (default is 2): ").strip() or "2"
    offsite = get_yes_no_input("Enable offsite following for CeWL? (yes/no): ")
    offsite_flag = "-o" if offsite else ""
    output_file = input("Enter the output file name for CeWL words (including extension): ").strip()
    verbose = get_yes_no_input("Enable verbose mode for CeWL? (yes/no): ")
    verbosity_flag = "-v" if verbose else ""

    command = f"cewl -d {depth} {offsite_flag} {verbosity_flag} -w {output_file} {url}"
    logging.info(f"Running CeWL with command: {command}")
    run_command(command.split())
    logging.info(f"CeWL output saved to: {output_file}")
    return output_file


def run_pipal(input_file: str) -> List[str]:
    """Run Pipal on the input file and generate the top 10 base words and passwords."""
    output_file = "pipal_output.txt"
    logging.info(f"Running Pipal on {input_file}...")
    run_command(["ruby", f"{PIPAL_DIR}/pipal.rb", input_file, "--output", output_file])

    if not os.path.exists(output_file):
        logging.error(f"Error: Pipal did not generate the expected output file: {output_file}")
        return []

    command = f"grep -A 10 'Top 10 passwords' {output_file} | tail -n +2 | awk -F '=' '{{print $1}}' | tr 'A-Z' 'a-z'"
    try:
        result = subprocess.check_output(command, shell=True, text=True)
        top_passwords = [password.strip() for password in result.splitlines() if password.strip()]
        logging.info(f"Top 10 passwords from Pipal: {top_passwords}")
        return top_passwords
    except subprocess.CalledProcessError as e:
        logging.error(f"Error processing Pipal output: {e}")
        return []


def seclists_source() -> Optional[str]:
    """Prompt user to choose between local SecLists, remote repository, or skip SecLists."""
    logging.info("Choose SecLists source or skip:")
    logging.info("1. Use locally installed SecLists (/usr/share/wordlists/seclists/Passwords/)")
    logging.info("2. Clone specific directories or files from the SecLists GitHub repository")
    logging.info("3. Skip SecLists")
    choice = input("Enter your choice (1/2/3): ").strip()

    if choice == "1":
        if os.path.exists(SECLISTS_LOCAL_DIR):
            files = []
            for root, _, filenames in os.walk(SECLISTS_LOCAL_DIR):
                for filename in filenames:
                    files.append(os.path.join(root, filename))
            for idx, filepath in enumerate(files, 1):
                logging.info(f"{idx}. {filepath}")

            selection = input("Enter the number corresponding to the file you want to use: ").strip()
            try:
                selected_file = files[int(selection) - 1]
                logging.info(f"Selected file: {selected_file}")
                return selected_file
            except (IndexError, ValueError):
                logging.error("Invalid selection. Please try again.")
                return seclists_source()
        else:
            logging.error(f"Local SecLists directory not found at {SECLISTS_LOCAL_DIR}.")
            return None

    elif choice == "2":
        logging.warning("Selective cloning from SecLists GitHub repository is not implemented yet.")
        return None

    elif choice == "3":
        logging.info("Skipping SecLists.")
        return None

    else:
        logging.error("Invalid choice. Please try again.")
        return seclists_source()


def collect_words_from_sources(cewl_file: Optional[str], seclists_file: Optional[str], pipal_passwords: List[str]) -> List[str]:
    """Collect words from CeWL, SecLists, and Pipal."""
    words = []
    if cewl_file:
        with open(cewl_file, 'r') as f:
            words.extend(line.strip() for line in f if line.strip())
    if seclists_file:
        with open(seclists_file, 'r') as f:
            words.extend(line.strip() for line in f if line.strip())
    if pipal_passwords:
        words.extend(pipal_passwords)
    return words


def generate_and_save_variants(words: List[str], patterns: List[str], output_file: str) -> None:
    """Generate password variants and save them to a file."""
    variants = generate_password_variants(words, patterns)
    with open(output_file, 'w') as f:
        for variant in variants:
            f.write(variant + '\n')
    logging.info(f"Generated {len(variants)} password combinations. Saved to {output_file}.")


def main() -> None:
    """Main script logic."""
    install_dependencies()

    cewl_file = cewl_crawl()
    seclists_file = seclists_source()
    pipal_passwords = run_pipal(cewl_file if cewl_file else seclists_file) if cewl_file or seclists_file else []

    words = collect_words_from_sources(cewl_file, seclists_file, pipal_passwords)

    additional_base_words_input = input("Enter additional base words, separated by commas: ").strip()
    additional_base_words = [word.strip().lower() for word in additional_base_words_input.split(",") if word.strip()]
    words.extend(additional_base_words)

    pattern_file = input("Enter the name of the pattern file (or press Enter to skip): ").strip()
    patterns = list(read_patterns(pattern_file)) if pattern_file else []

    logging.info("\nSummary of files used for word combination:")
    logging.info(f"CeWL file used: {cewl_file if cewl_file else 'None'}")
    logging.info(f"SecLists file used: {seclists_file if seclists_file else 'None'}")
    logging.info(f"Pipal top 10 passwords: {', '.join(pipal_passwords) if pipal_passwords else 'None'}")
    logging.info(f"Additional base words: {', '.join(additional_base_words) if additional_base_words else 'None'}")

    proceed = get_yes_no_input("Do you want to proceed with generating password combinations? (yes/no): ")
    if proceed:
        output_file = input("Enter the output file path: ").strip()
        generate_and_save_variants(words, patterns, output_file)
    else:
        logging.info("Exiting without generating combinations.")


if __name__ == "__main__":
    main()
