# Contributing to GSP-Py

Thank you for considering contributing to **GSP-Py**, a Python implementation of the Generalized Sequential Pattern algorithm! Contributions, whether they're reporting bugs, suggesting improvements, or submitting code, are greatly appreciated. Please review this document to understand how you can contribute effectively.

---

## How Can You Contribute?

Here are some ways to contribute to the project:
1. **Report Bugs**: If you encounter any issues, please let us know by submitting a bug report.
2. **Suggest Enhancements**: Suggest new features or improvements.
3. **Fix Bugs or Add Features**: Help fix issues or implement features based on the project's roadmap or your own ideas.
4. **Improve Documentation**: Correct typos, add usage examples, or expand explanations in the documentation.
5. **Write Tests**: Testing is an essential component to ensure a reliable library.

---

## Workflow for Contributors

If you'd like to contribute code or documentation, please follow these steps:

### **1. Fork the Repository**
- Visit the [GSP-Py repository](https://github.com/jacksonpradolima/gsp-py) and click "Fork."

### **2. Clone the Fork**
Clone the forked repository to your local machine:
```bash
git clone https://github.com/<your-username>/gsp-py.git
cd gsp-py
```

### **3. Create a New Branch**
Create a new branch for your work:
```bash
git checkout -b feature/my-feature
```
Use a descriptive branch name, such as `fix/issue-123` or `feature/custom-filter-support`.

### **4. Make Changes**
- Edit and test your code locally.
- Ensure any new features include unit tests.

### **5. Run Tests**
Before submitting your changes, ensure the code passes all tests:
```bash
pytest
```

If you're adding a new feature, include tests for it in the `tests/` directory.

### **6. Push Changes**
Push your changes to your forked repository:
```bash
git add .
git commit -m "Add a brief but descriptive commit message"
git push origin feature/my-feature
```

### **7. Submit a Pull Request (PR)**
- Navigate to the main repository's GitHub page and select **Pull Requests**.
- Click **New Pull Request** and provide details about your changes, including:
  - A clear summary of your contribution.
  - Any relevant references (e.g., a related issue or feature request).
- Be sure to reference the associated issue (if applicable) in your PR description (e.g., "Closes #12").

---

## Coding Standards and Guidelines

To maintain consistency and code quality, please follow these coding guidelines:

1. **Formatting**:
   - Follow [PEP 8](https://peps.python.org/pep-0008/) for Python code style conventions.
   - Use tools like `pylint` or `flake8` to ensure your code is formatted correctly:
     ```bash
     pylint path/to/file.py
     ```

2. **Commit Messages**:
   - Write clear and concise commit messages.
   - Begin your commit message with an action verb, such as "Add," "Fix," "Improve," "Update," etc.
   - For example: `Fix candidate pruning for short sequences`.

3. **Tests**:
   - Write tests for new features or bug fixes.
   - Use `pytest` as the testing framework.
   - Place tests in the `tests/` directory using descriptive test names.

4. **Documentation**:
   - Update documentation (`README.md`, `CHANGELOG.md`, comments in code) related to your changes.
   - If a new feature is added, provide usage examples and explanation.

---

## Getting Started with the Codebase

To get familiar with the existing code, follow these steps:

1. **Setup Environment**:
   This project uses [Rye](https://github.com/mitsuhiko/rye) for managing dependencies and the virtual environment. Follow these instructions to set it up:

   - Install Rye (if not already installed):
     ```bash
     curl -sSf https://rye.astral.sh/get | bash
     ```

     Make sure Rye's binary directory is added to your `PATH`:
     ```bash
     export PATH="$HOME/.rye/bin:$PATH"
     ```

   - Install project dependencies using Rye:
     ```bash
     rye sync
     ```

     This command reads the dependencies specified in the `pyproject.toml` file and installs them into a local environment managed by Rye.

2. **Run Tests**:
   Use Rye to run tests and verify the baseline state:
   ```bash
   rye run test
   ```

   The `test` script is defined in the `pyproject.toml` under `[tool.rye.scripts]` and uses `pytest`.

3. **Explore the Code**:
   The main entry point for the GSP algorithm is in the `gsppy` module. The libraries for support counting, candidate generation, and additional utility functions are also within this module.

---

### Notes:
- No need to create a `venv` or install dependencies manually with `pip`; Rye handles everything based on the `pyproject.toml` file.
- If you’re unfamiliar with Rye, refer to its [documentation](https://github.com/mitsuhiko/rye).

## Reporting Issues

To report a bug or suggest an enhancement, open an issue on GitHub:

1. **Go to the [Issues](https://github.com/jacksonpradolima/gsp-py/issues) page**.
2. Select **New Issue** and choose the appropriate issue template:
   - Bug report
   - Feature request
3. Include as much detail as possible:
   - Steps to reproduce (for bugs).
   - Clear description of the feature or enhancement (for feature requests).

---

## Feedback

We welcome all suggestions or feedback for improving this project! You can reach out by opening an issue or submitting a pull request.

Let’s build a great tool together! 😊

---

## Code of Conduct

Please note that this project adheres to the [Contributor Covenant Code of Conduct](https://www.contributor-covenant.org/version/2/1/code_of_conduct/). By participating, you are expected to uphold this code. Please report unacceptable behavior to the project maintainer.

---

Thank you for contributing! 🙌
