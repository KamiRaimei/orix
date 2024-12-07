# Orix

A powerful wordlist generation tool for pentesting, combining **CeWL**, **Pipal**, and **SecLists**. Orix provides a robust and efficient pipeline for collecting, analyzing, and generating highly customized wordlists from multiple sources such as websites, password patterns, and more.

**Note**: This project is created for **educational and experimental purposes** only. Please use it responsibly and ensure you have proper authorization before using it in any pentesting scenarios.

---

## Features

- **Dependency Auto-Installation**:
  - Automatically detects your Linux distribution (Arch, Debian/Ubuntu, Fedora).
  - Installs necessary dependencies like **CeWL**, **Ruby**, and **Pipal** (best effort).

- **CeWL Integration**:
  - Crawl websites to generate wordlists.
  - Options for offsite following and verbose output.
  - Automatically saves results to a CeWL output file.

- **Pipal Integration**:
  - Analyze password lists to extract the top 10 most common passwords.
  - Automatically integrates Pipal results into the wordlist generation logic.

- **Local and Remote SecLists**:
  - Use SecLists from `/usr/share/wordlists/seclists` (if available).
  - Option to selectively clone specific directories or files from the SecLists GitHub repository.

- **Dynamic Wordlist Generation**:
  - Leverages:
    - Leet speak variants (`@` for `a`, `3` for `e`, etc.).
    - Common patterns (years, special characters, sequences).
    - Reversals, camel case, and duplications.
  - Combines words from all sources, including CeWL, Pipal, and user-provided patterns.

- **Interactive Workflow**:
  - Displays a summary of all inputs (CeWL, Pipal, SecLists, and user-provided words).
  - Prompts for confirmation before generating combinations.
  - Verbose progress for all major steps.

---

## Requirements

- Python 3.x
- Supported Linux distributions:
  - **Arch Linux**: Full automation for dependency installation.
  - **Debian/Ubuntu**: Supports automated setup via `apt`.
  - **Fedora**: Supports automated setup via `dnf`.
  - Other distributions may require manual setup.

---

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/KamiRaimei/orix.git
   cd orix
   ```
2. Run the script:

    ```bash
    Copy code
    python3 orix.py
    ```
3. The script will:

    - Detect your Linux distribution.
    - Attempt to install missing dependencies automatically.


## Usage
1. Run the Script:

  ```bash
    python3 orix.py
  ```
2. Follow the Prompts:

    - Crawl websites using CeWL.
    - Use SecLists (local or remote).
    - Analyze files with Pipal.
    - Add custom base words or patterns.

3. Generate Your Wordlist:

    - Combines all sources and patterns into a custom wordlist.
    - Automatically handles variations (leet speak, sequences, etc.).
    - Saves the results to your specified output file.

## Contributions
This project is a personal side project and a learning experience. Contributions, feedback, and suggestions are welcome! Feel free to submit a pull request or open an issue.

## License
This project is licensed under the MIT License.

## Acknowledgments

- **CeWL**: [CeWL on GitHub](https://github.com/digininja/CeWL)  
- **Pipal**: [Pipal on GitHub](https://github.com/digininja/pipal)  
- **SecLists**: [SecLists on GitHub](https://github.com/danielmiessler/SecLists)  
