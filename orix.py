import os
import subprocess
import itertools


def install_dependencies():
    """Install Pipal dependencies and optionally install CeWL for Arch Linux."""
    print("Checking for first-run setup...")
    setup_pipal = input("Do you want to download and setup Pipal dependencies? (yes/no): ").strip().lower()
    if setup_pipal in {'yes', 'y'}:
        pipal_repo = "https://github.com/digininja/pipal.git"
        pipal_dir = "./pipal"

        if not os.path.exists(pipal_dir):
            print(f"Cloning Pipal repository from {pipal_repo}...")
            subprocess.run(f"git clone {pipal_repo} {pipal_dir}", shell=True)
        else:
            print("Pipal directory already exists. Skipping cloning.")

        print("Ensuring Ruby is installed...")
        subprocess.run("sudo pacman -S --noconfirm ruby", shell=True)
        print("Ruby installed.")

    install_cewl = input("Do you want to install CeWL? (yes/no): ").strip().lower()
    if install_cewl in {'yes', 'y'}:
        print("Installing CeWL using Arch Linux's package manager...")
        subprocess.run("sudo pacman -S --needed --noconfirm cewl", shell=True)
        print("CeWL installed.")


def read_patterns(pattern_file):
    """Read patterns from the given file and return as a list."""
    try:
        with open(pattern_file, 'r') as f:
            patterns = [line.strip() for line in f if line.strip()]
            print(f"Found {len(patterns)} patterns in {pattern_file}.")
            return patterns
    except FileNotFoundError:
        print(f"Error: The file {pattern_file} does not exist.")
        exit()
    except Exception as e:
        print(f"An error occurred while reading {pattern_file}: {e}")
        exit()


def leet_speak_variants(word):
    """Generate leet speak variants for a given word."""
    replacements = {'a': '@', 'e': '3', 'i': '1', 'o': '0', 's': '$'}
    variants = {word}
    for char, replacement in replacements.items():
        if char in word:
            variants.add(word.replace(char, replacement))
    return variants


def generate_password_variants(words, patterns):
    """Generate password-like variants for each word using the patterns."""
    variants = set(words)
    years = ['2023', '2024']
    special_chars = ['!', '@', '#', '$', '%']
    number_sequences = ['123', '1234', '12345']

    for word in words:
        # Add leet speak variants
        variants.update(leet_speak_variants(word))

        # Add common combinations
        for pattern in patterns:
            variants.add(word + pattern)
            variants.add(pattern + word)

        # Add years, special characters, and number sequences
        for item in years + special_chars + number_sequences:
            variants.add(word + item)
            variants.add(item + word)

        # Add duplication, reversal, and camel case
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


def cewl_crawl():
    """Prompt user for CeWL options and perform web crawling."""
    use_cewl = input("Would you like to use CeWL to crawl a website for passwords? (yes/no): ").strip().lower()
    if use_cewl in {'yes', 'y'}:
        url = input("Enter the URL to crawl: ").strip()
        depth = input("Enter crawl depth (default is 2): ").strip() or "2"
        offsite = input("Enable offsite following for CeWL? (yes/no): ").strip().lower()
        offsite_flag = "-o" if offsite in {'yes', 'y'} else ""
        output_file = input("Enter the output file name for CeWL words (including extension): ").strip()
        verbose = input("Enable verbose mode for CeWL? (yes/no): ").strip().lower()
        verbosity_flag = "-v" if verbose in {'yes', 'y'} else ""

        command = f"cewl -d {depth} {offsite_flag} {verbosity_flag} -w {output_file} {url}"
        print(f"Running CeWL with command: {command}")
        subprocess.run(command, shell=True)
        print(f"CeWL output saved to: {output_file}")
        return output_file
    return None


def run_pipal(input_file):
    """Run Pipal on the input file and generate the top 10 base words and passwords."""
    pipal_repo = "./pipal"
    output_file = "pipal_output.txt"

    # Run Pipal on the given file and generate the output
    print(f"Running Pipal on {input_file}...")
    result = subprocess.run(f"ruby {pipal_repo}/pipal.rb {input_file} --output {output_file}", shell=True, capture_output=True)

    # Check if Pipal ran successfully and generated output
    if result.returncode != 0:
        print(f"Error running Pipal. Output:\n{result.stderr.decode()}")
        return []

    # Verify that the output file was created
    if not os.path.exists(output_file):
        print(f"Error: Pipal did not generate the expected output file: {output_file}")
        return []

    # Process the Pipal output to extract the top 10 passwords
    command = f"grep -A 10 'Top 10 passwords' {output_file} | tail -n +2 | awk -F '=' '{{print $1}}' | tr 'A-Z' 'a-z'"
    try:
        result = subprocess.check_output(command, shell=True, text=True)
        # Split the result into a list of passwords (strip any extra spaces or newlines)
        top_passwords = [password.strip() for password in result.splitlines() if password.strip()]
        print(f"Top 10 passwords from Pipal: {top_passwords}")
        return top_passwords
    except subprocess.CalledProcessError as e:
        print(f"Error processing Pipal output: {e}")
        return []

def seclists_source():
    """Prompt user to choose between local SecLists, remote repository, or skip SecLists."""
    print("Choose SecLists source or skip:")
    print("1. Use locally installed SecLists (/usr/share/wordlists/seclists/Passwords/)")
    print("2. Clone specific directories or files from the SecLists GitHub repository")
    print("3. Skip SecLists")
    choice = input("Enter your choice (1/2/3): ").strip()

    if choice == "1":
        local_dir = "/usr/share/wordlists/seclists/Passwords/"
        if os.path.exists(local_dir):
            print(f"Scanning available files and directories in: {local_dir}")
            files = []
            for root, dirs, filenames in os.walk(local_dir):
                for filename in filenames:
                    files.append(os.path.join(root, filename))
            for idx, filepath in enumerate(files, 1):
                print(f"{idx}. {filepath}")

            selection = input("Enter the number corresponding to the file you want to use: ").strip()
            try:
                selected_file = files[int(selection) - 1]
                print(f"Selected file: {selected_file}")
                return selected_file
            except (IndexError, ValueError):
                print("Invalid selection. Please try again.")
                return seclists_source()
        else:
            print(f"Local SecLists directory not found at {local_dir}.")
            return None

    elif choice == "2":
        return selective_seclists_clone()

    elif choice == "3":
        print("Skipping SecLists.")
        return None

    else:
        print("Invalid choice. Please try again.")
        return seclists_source()

def main():
    """Main script logic."""
    # Install dependencies (Pipal, CeWL)
    install_dependencies()

    # Crawl website with CeWL
    cewl_file = cewl_crawl()

    # Choose and load SecLists file (optional)
    seclists_file = seclists_source()

    # Get Pipal top 10 passwords
    pipal_passwords = run_pipal(cewl_file if cewl_file else seclists_file)  # Assuming we use CeWL file if available

    # Prompt user for additional base words
    additional_base_words_input = input("Enter additional base words, separated by commas: ").strip()
    additional_base_words = [word.strip().lower() for word in additional_base_words_input.split(",") if word.strip()]

    # Read user-provided pattern file
    pattern_file = input("Enter the name of the pattern file (or press Enter to skip): ").strip()
    patterns = read_patterns(pattern_file) if pattern_file else []

    # Collect words from all sources
    words = []
    if cewl_file:
        with open(cewl_file, 'r') as f:
            words.extend([line.strip() for line in f if line.strip()])
    if seclists_file:
        with open(seclists_file, 'r') as f:
            words.extend([line.strip() for line in f if line.strip()])
    if pipal_passwords:
        words.extend(pipal_passwords)
    if additional_base_words:
        words.extend(additional_base_words)

    # Generate password variants
    variants = generate_password_variants(words, patterns)

    # Display a summary of input files used
    print("\nSummary of files used for word combination:")
    print(f"CeWL file used: {cewl_file if cewl_file else 'None'}")
    print(f"SecLists file used: {seclists_file if seclists_file else 'None'}")
    print(f"Pipal top 10 passwords: {', '.join(pipal_passwords) if pipal_passwords else 'None'}")
    print(f"Additional base words: {', '.join(additional_base_words) if additional_base_words else 'None'}")

    proceed = input("Do you want to proceed with generating password combinations? (yes/no): ").strip().lower()
    if proceed in {'yes', 'y'}:
        output_file = input("Enter the output file path: ").strip()
        with open(output_file, 'w') as f:
            for variant in variants:
                f.write(variant + '\n')

        print(f"Generated {len(variants)} password combinations. Saved to {output_file}.")
    else:
        print("Exiting without generating combinations.")

if __name__ == "__main__":
    main()