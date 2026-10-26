# rdkbmesh-zap

## Description

**rdkbmesh-zap** is a python-based plugin repo of zaero framework targeted to test RDKB Mesh Nodes.

---

## Prerequisites

Make sure you have the following installed:

* zaero package - https://github.com/zilogic-systems/zaero

---

## Installation

### 1. Clone the Repository

```
git clone https://github.com/zilogic-systems/rdkbmesh-zap.git
```

### 2. Generate .whl file

```
python3 -m pip install build
cd rdkbmesh-zap
python3 -m build
```

### 3. Install rdkbmeshzap Package

```
cd dist/
python3 -m pip install rdkbmeshzap-<version>-py3-none-any.whl
```

---
### 4. Fetch infra.yaml from zaero to rdkbmeshzap

```
cd ../test/config
python3 -m zaero init_config
```
Note: infra.yaml should be present in EM-RDKB-ZaP/test/config/ directory

---

## Configuration

### Fields to Fill in `infra.yaml and platform.yaml`

Before running the test_suite / test_file, update the required parameters :
1) `/test/config/infra.yaml` with your test-bed specific values.
2) `/test/config/platform.yaml` with your platform specific values.

---

## Enabling Device Permission (dialout group access)

### 1. Add the current user to the `dialout` group (needed for serial/USB device access):
   ```
   sudo usermod -aG dialout $USER
   ```
### 2. Apply the new group membership immediately:
   ```
   newgrp dialout
   ```
### 3. Restart the Test Machine to reflect changes.

---

## Enabling Root Access (on Client Device)

### 1. Open the SSH daemon configuration file:
   ```
   sudo cat /etc/ssh/sshd_config
   ```
   (Use `sudo nano /etc/ssh/sshd_config` to edit it directly)

### 2. Find the line `PermitRootLogin` and set it to:
   ```
   PermitRootLogin yes
   ```

### 3. Restart the SSH service so the change takes effect:
   ```
   sudo systemctl restart ssh
   ```

### 4. Switch to the root user:
   ```
   sudo su
   ```

### 5. Set the root password:
   ```
   passwd
   ```

Once this is done, root login will be enabled for any future SSH connections into this device.

---

## Usage

### Select an Execution Mode

Test selection is controlled by `test/config/platform.yaml`:

```yaml
test_parameters:
   execution_mode: terminal
```

The supported values are:

* `terminal` - Opens an interactive console selector using Questionary. Select suites and test cases from the terminal, then choose **Run Validation**.
* `browser` - Starts the Streamlit dashboard in a browser. Select suites and individual test cases through the UI, then click **Run Validation**.

### Launch the Test Selector

Run the launcher from the project root:

```
python3 trigger_test.py
```

The launcher reads `execution_mode` and starts the corresponding selector. Both modes execute the selected test files through pytest and generate an HTML report under `Reports/TestRun_<timestamp>/report.html`.

For browser mode, Streamlit must be installed with the project dependencies. The dashboard is located at `test_dashboard/test_dashboard.py` and can also be started directly:

```
python3 -m streamlit run test_dashboard/test_dashboard.py
```

`main.py` contains the reusable test execution function used by the launcher and dashboard; use `trigger_test.py` as the normal entry point.

---

## Author

Zilogic Systems
