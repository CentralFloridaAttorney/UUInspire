import json
import os
import subprocess
import threading
import traceback
import webbrowser
import yaml
from datetime import datetime
from tkinter import filedialog, simpledialog, ttk

import tkinter as tk


def get_default_params():
    return {
        "Behavior Name": "CoinCollectorAgent",
        "Trainer Type": "ppo",
        "Batch Size": 64,
        "Buffer Size": 2048,
        "Learning Rate": 0.0003,
        "Beta": 0.0005,
        "Epsilon": 0.2,
        "Lambd": 0.95,
        "Num Epoch": 3,
        "Learning Rate Schedule": "linear",
        "Normalize": "true",
        "Hidden Units": 128,
        "Num Layers": 2,
        "Visual Encoder Type": "simple",
        "Extrinsic Gamma": 0.99,
        "Extrinsic Strength": 1.0,
        "Curiosity Strength": 0.01,
        "Curiosity Gamma": 0.99,
        "Curiosity Encoding Size": 256,
        "Max Steps": 500000,
        "Time Horizon": 64,
        "Summary Frequency": 10000,
        "Checkpoint Interval": 500000,
        "Keep Checkpoints": 5,
        "Threaded": "true"
    }


def save_yaml_file(config, output_file):
    with open(output_file, 'w') as file:
        yaml.safe_dump(config, file)


class ZTrainer:
    def __init__(self, config_path, run_name, conda_env_name, mlagents_learn_path="mlagents-learn",
                 executable_path=None, no_graphics=False, time_scale=False):
        self.config_path = config_path
        self.run_name = run_name
        self.conda_env_name = conda_env_name
        self.mlagents_learn_path = mlagents_learn_path
        self.executable_path = executable_path
        self.no_graphics = no_graphics
        self.time_scale = time_scale
        self.process = None
        self.threads = []

    def start_training(self, callback):
        thread = threading.Thread(target=self._start_training_process, args=(callback,))
        thread.start()
        self.threads.append(thread)

    def _start_training_process(self, callback):
        try:
            if not os.access(self.config_path, os.R_OK):
                raise PermissionError(f"Read permission denied for config file: {self.config_path}")

            cmd = f"conda run -n {self.conda_env_name} {self.mlagents_learn_path} {self.config_path} --run-id={self.run_name} --base-port=5005 --results-dir=results --force"

            if self.executable_path:
                cmd = f"{cmd} --env {self.executable_path}"
            if self.no_graphics:
                cmd = f"{cmd} --no-graphics"
            if self.time_scale:
                cmd = f"{cmd} --time-scale"

            if os.name == 'nt':
                self.process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True, creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
            else:
                self.process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True, preexec_fn=os.setsid)

            self._read_process_output(callback)
        except PermissionError as pe:
            callback(f"Permission Error: {pe}")
        except Exception as e:
            callback(f"Failed to start training: {e}\n{traceback.format_exc()}")

    def _read_process_output(self, callback):
        try:
            for line in self.process.stdout:
                callback(line)
            for line in self.process.stderr:
                callback(line)
        except Exception as e:
            callback(f"Error reading process output: {e}\n{traceback.format_exc()}")

    def stop(self):
        if self.process and self.process.poll() is None:
            self.process.terminate()
        for thread in self.threads:
            thread.join()


class ZTensorBoardManager:
    def __init__(self, conda_env_name):
        self.conda_env_name = conda_env_name
        self.process = None
        self.threads = []

    def start_tensorboard(self, callback):
        thread = threading.Thread(target=self._start_tensorboard_process, args=(callback,))
        thread.start()
        self.threads.append(thread)

    def _start_tensorboard_process(self, callback):
        try:
            cmd = f"conda run -n {self.conda_env_name} tensorboard --logdir=results --port=6006"
            self.process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, text=True)
            self._read_process_output(callback)
            webbrowser.open("http://localhost:6006")
        except Exception as e:
            callback(f"Failed to start TensorBoard: {e}")

    def _read_process_output(self, callback):
        try:
            for line in self.process.stdout:
                callback(line)
            for line in self.process.stderr:
                callback(line)
        except Exception as e:
            callback(f"Error reading process output: {e}")

    def stop(self):
        if self.process and self.process.poll() is None:
            self.process.terminate()
        for thread in self.threads:
            thread.join()


class ConfigGenerator:
    def __init__(self, params=None, yaml_file=None, num_behaviors=1):
        self.yaml_file = yaml_file
        self.params = params or get_default_params()
        self.num_behaviors = num_behaviors
        if yaml_file:
            self.config = self.load_yaml_file()
        else:
            self.config = self.create_config_structure()
            self.save_yaml_file("training_config.yaml")

    def create_config_structure(self):
        config = {'behaviors': {}}
        for i in range(self.num_behaviors):
            behavior_name = f"{self.params['Behavior Name']}_{i + 1}"
            config['behaviors'][behavior_name] = self.get_behavior_structure(behavior_name)
        return config

    def get_behavior_structure(self, behavior_name):
        return {
            'trainer_type': self.params["Trainer Type"],
            'hyperparameters': {
                'batch_size': int(self.params["Batch Size"]),
                'buffer_size': int(self.params["Buffer Size"]),
                'learning_rate': float(self.params["Learning Rate"]),
                'beta': float(self.params["Beta"]),
                'epsilon': float(self.params["Epsilon"]),
                'lambd': float(self.params["Lambd"]),
                'num_epoch': int(self.params["Num Epoch"]),
                'learning_rate_schedule': self.params["Learning Rate Schedule"],
            },
            'network_settings': {
                'normalize': self.params["Normalize"].lower() == 'true',
                'hidden_units': int(self.params["Hidden Units"]),
                'num_layers': int(self.params["Num Layers"]),
                'vis_encode_type': self.params["Visual Encoder Type"],
            },
            'reward_signals': {
                'extrinsic': {
                    'gamma': float(self.params["Extrinsic Gamma"]),
                    'strength': float(self.params["Extrinsic Strength"]),
                },
                'curiosity': {
                    'strength': float(self.params["Curiosity Strength"]),
                    'gamma': float(self.params["Curiosity Gamma"]),
                    'network_settings': {
                        'encoding_size': int(self.params["Curiosity Encoding Size"]),
                    },
                }
            },
            'max_steps': int(self.params["Max Steps"]),
            'time_horizon': int(self.params["Time Horizon"]),
            'summary_freq': int(self.params["Summary Frequency"]),
            'checkpoint_interval': int(self.params["Checkpoint Interval"]),
            'keep_checkpoints': int(self.params["Keep Checkpoints"]),
            'threaded': self.params["Threaded"].lower() == 'true',
        }

    def load_yaml_file(self):
        if not self.yaml_file:
            raise ValueError("YAML file path not provided.")
        with open(self.yaml_file, 'r') as file:
            self.config = yaml.safe_load(file)
        return self.config

    def save_yaml_file(self, output_file=None):
        if not output_file:
            main_key = next(iter(self.config))
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"{main_key}_{timestamp}.yaml"
        save_yaml_file(self.config, output_file)

    def set_value(self, pathlikekey, value):
        keys = pathlikekey.split('.')
        current = self.config
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        current[keys[-1]] = value

    def rename_behavior(self, old_name, new_name):
        if old_name in self.config['behaviors']:
            self.config['behaviors'][new_name] = self.config['behaviors'][old_name].copy()
            del self.config['behaviors'][old_name]


class GUISetup:
    def __init__(self, root, choose_file_callback, apply_settings_callback, start_training_callback,
                 start_tensorboard_callback, choose_conda_env_callback, choose_executable_callback):
        self.root = root
        self.root.title("ML-Agents Trainer")

        # Add buttons and entries for the callbacks
        self.choose_file_button = ttk.Button(root, text="Choose Config File", command=choose_file_callback)
        self.choose_file_button.grid(row=0, column=0, padx=10, pady=10)

        self.conda_env_label = ttk.Label(root, text="Conda Environment:")
        self.conda_env_label.grid(row=1, column=0, padx=10, pady=10)
        self.conda_env_entry = ttk.Entry(root)
        self.conda_env_entry.grid(row=1, column=1, padx=10, pady=10)
        self.conda_env_button = ttk.Button(root, text="Select Conda Env", command=choose_conda_env_callback)
        self.conda_env_button.grid(row=1, column=2, padx=10, pady=10)

        self.executable_label = ttk.Label(root, text="Unity Executable:")
        self.executable_label.grid(row=2, column=0, padx=10, pady=10)
        self.executable_entry = ttk.Entry(root)
        self.executable_entry.grid(row=2, column=1, padx=10, pady=10)
        self.executable_button = ttk.Button(root, text="Select Executable", command=choose_executable_callback)
        self.executable_button.grid(row=2, column=2, padx=10, pady=10)

        # Other buttons and entries
        self.run_name_label = ttk.Label(root, text="Run Name:")
        self.run_name_label.grid(row=3, column=0, padx=10, pady=10)
        self.run_name_entry = ttk.Entry(root)
        self.run_name_entry.grid(row=3, column=1, padx=10, pady=10)

        self.apply_settings_button = ttk.Button(root, text="Apply Settings", command=apply_settings_callback)
        self.apply_settings_button.grid(row=4, column=0, padx=10, pady=10)

        self.start_training_button = ttk.Button(root, text="Start Training", command=start_training_callback)
        self.start_training_button.grid(row=5, column=0, padx=10, pady=10)

        self.start_tensorboard_button = ttk.Button(root, text="Start TensorBoard", command=start_tensorboard_callback)
        self.start_tensorboard_button.grid(row=5, column=1, padx=10, pady=10)

        # Console output
        self.console_output = tk.Text(root, height=15, width=80)
        self.console_output.grid(row=6, column=0, columnspan=3, padx=10, pady=10)

        self.status_label = ttk.Label(root, text="Status: Ready")
        self.status_label.grid(row=7, column=0, columnspan=3, padx=10, pady=10)

        self.num_behaviors_label = ttk.Label(root, text="Number of Behaviors:")
        self.num_behaviors_label.grid(row=8, column=0, padx=10, pady=10)
        self.num_behaviors_entry = ttk.Entry(root)
        self.num_behaviors_entry.grid(row=8, column=1, padx=10, pady=10)
        self.num_behaviors_entry.insert(0, '1')  # Set a default value

        self.no_graphics_var = tk.BooleanVar()
        self.no_graphics_checkbox = ttk.Checkbutton(root, text="No Graphics", variable=self.no_graphics_var)
        self.no_graphics_checkbox.grid(row=9, column=0, padx=10, pady=5, sticky=tk.W)

        self.time_scale_var = tk.BooleanVar()
        self.time_scale_checkbox = ttk.Checkbutton(root, text="Time Scale", variable=self.time_scale_var)
        self.time_scale_checkbox.grid(row=9, column=1, padx=10, pady=5, sticky=tk.W)

        self.second_frame = ttk.Frame(root)
        self.second_frame.grid(row=10, column=0, columnspan=3, padx=10, pady=10)
        self.scrollbar = ttk.Scrollbar(self.second_frame, orient=tk.VERTICAL)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas = tk.Canvas(self.second_frame, yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.canvas.yview)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.scrollable_frame = ttk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        self.entries = {}
        self.entry_rows = {}

        self.add_tensorboard_link()

    def update_scroll_region(self):
        if self.canvas.winfo_exists():
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def update_console_output(self, text):
        self.console_output.insert(tk.END, text + '\n')
        self.console_output.see(tk.END)

    def update_run_name(self, config_path):
        run_name = os.path.splitext(os.path.basename(config_path))[0]
        self.run_name_entry.delete(0, tk.END)
        self.run_name_entry.insert(0, run_name)

    def add_tensorboard_link(self):
        hyperlink_text = "TensorBoard: http://localhost:6006"
        self.console_output.insert(tk.END, hyperlink_text)
        self.console_output.tag_add("hyperlink", "1.12", "1.37")
        self.console_output.tag_config("hyperlink", foreground="blue", underline=True)
        self.console_output.tag_bind("hyperlink", "<Button-1>", lambda e: webbrowser.open("http://localhost:6006"))
        self.console_output.insert(tk.END, "\n")
        self.console_output.see(tk.END)


class MLAgentApp:
    SETTINGS_FILE = 'ml_agent_settings.json'

    def __init__(self, root):
        self.config_generator = None
        self.root = root
        self.config_path = None
        self.conda_env_name = "mlagents_env"  # Default conda environment name
        self.mlagents_learn_path = "mlagents-learn"  # Default path for mlagents-learn
        self.executable_path = None  # Path to the Unity executable

        self.gui = GUISetup(
            root,
            self.choose_file,
            self.apply_settings,
            self.start_training_thread,
            self.start_tensorboard_thread,
            self.choose_conda_env_name,
            self.choose_executable
        )

        self.trainer = None
        self.tensorboard_manager = None

        # Create default configuration after GUI setup is complete
        self.root.after(100, self.create_default_config)

    def create_default_config(self):
        try:
            num_behaviors = int(self.gui.num_behaviors_entry.get())
        except ValueError:
            num_behaviors = 1  # Set a default value if the entry is empty or invalid
            self.gui.num_behaviors_entry.insert(0, str(num_behaviors))  # Update the entry with the default value

        self.config_generator = ConfigGenerator(num_behaviors=num_behaviors)
        default_config = self.config_generator.config
        self.create_gui_elements(default_config)

        # Load settings from the settings file
        self.load_settings()

    def create_gui_elements(self, config):
        for widget in self.gui.scrollable_frame.winfo_children():
            widget.destroy()

        self.gui.entries = {}
        self.gui.entry_rows = {}

        row = 0
        for behavior_name, behavior_params in config['behaviors'].items():
            behavior_label = ttk.Label(self.gui.scrollable_frame, text=f"Behavior: {behavior_name}",
                                       font=("Helvetica", 14, "bold"))
            behavior_label.grid(column=0, row=row, columnspan=2, padx=5, pady=5, sticky=tk.W)

            behavior_entry = ttk.Entry(self.gui.scrollable_frame)
            behavior_entry.grid(column=1, row=row, padx=5, pady=5, sticky=tk.W)
            behavior_entry.insert(0, behavior_name)
            behavior_entry.bind("<FocusOut>",
                                lambda e, old_name=behavior_name, entry=behavior_entry: self.update_behavior_name(
                                    old_name, entry.get()))

            delete_button = ttk.Button(self.gui.scrollable_frame, text="Delete Behavior",
                                       command=lambda bn=behavior_name: self.delete_behavior(bn))
            delete_button.grid(column=2, row=row, padx=5, pady=5)

            row += 1

            for section, section_params in behavior_params.items():
                if isinstance(section_params, dict):
                    for param, value in section_params.items():
                        self.create_label_and_entry(f"{behavior_name}.{section}.{param}", value, row)
                        row += 1
                else:
                    self.create_label_and_entry(f"{behavior_name}.{section}", section_params, row)
                    row += 1

        self.gui.update_scroll_region()

    def create_label_and_entry(self, label_text, default_value, row, is_behavior_name=False):
        label = ttk.Label(self.gui.scrollable_frame, text=label_text)
        label.grid(column=0, row=row, padx=5, pady=5, sticky=tk.W)

        entry = ttk.Entry(self.gui.scrollable_frame)
        entry.grid(column=1, row=row, padx=5, pady=5, sticky=tk.W)
        entry.insert(0, default_value)

        if is_behavior_name:
            entry.bind("<FocusOut>", lambda e, lt=label_text: self.update_behavior_name(lt, entry.get()))

        self.gui.entries[label_text] = entry
        self.gui.entry_rows[label_text] = row

    def update_behavior_name(self, old_name, new_name):
        if old_name != new_name:
            self.config_generator.rename_behavior(old_name, new_name)
            self.save_and_reload_config()

    def save_and_reload_config(self):
        run_name = self.gui.run_name_entry.get() or "default_run"
        output_file = os.path.join(os.getcwd(), f"{run_name}_config.yaml")
        self.config_generator.save_yaml_file(output_file)
        self.load_config(output_file)

    def choose_file(self):
        self.config_path = filedialog.askopenfilename(title="Select Default Config File",
                                                      filetypes=[("YAML files", "*.yaml"), ("All files", "*.*")])
        if self.config_path:
            self.gui.update_console_output(f"Selected zmlagent file: {self.config_path}")
            self.load_config(self.config_path)
            self.gui.update_run_name(self.config_path)  # Update the run name based on the selected file

            # Load settings from the settings file
            self.load_settings()

    def choose_conda_env_name(self):
        env_name = simpledialog.askstring(
            title="Select Conda Environment Name",
            prompt="Enter the name of the Conda environment:"
        )
        if env_name:
            self.conda_env_name = env_name  # Store the environment name
            self.gui.update_console_output(f"Selected Conda Environment: {env_name}")
            self.gui.conda_env_entry.delete(0, tk.END)
            self.gui.conda_env_entry.insert(0, env_name)

    def choose_executable(self):
        self.executable_path = filedialog.askopenfilename(title="Select Unity Executable",
                                                          filetypes=[("Executable files", "*.exe *.x86_64"),
                                                                     ("All files", "*.*")])
        if self.executable_path:
            self.gui.update_console_output(f"Selected Unity Executable: {self.executable_path}")
            self.gui.executable_entry.delete(0, tk.END)
            self.gui.executable_entry.insert(0, self.executable_path)

    def load_config(self, path):
        self.config_generator = ConfigGenerator(yaml_file=path)
        config_data = self.config_generator.load_yaml_file()
        try:
            num_behaviors = int(self.gui.num_behaviors_entry.get())
        except ValueError:
            num_behaviors = 1
            self.gui.num_behaviors_entry.insert(0, str(num_behaviors))

        current_behaviors = list(config_data['behaviors'].keys())
        current_count = len(current_behaviors)

        if current_count < num_behaviors:
            for i in range(current_count, num_behaviors):
                new_behavior_name = f"{self.config_generator.params['Behavior Name']}_{i + 1}"
                config_data['behaviors'][new_behavior_name] = self.config_generator.get_behavior_structure(
                    new_behavior_name)
        elif current_count > num_behaviors:
            for i in range(current_count - num_behaviors):
                del config_data['behaviors'][current_behaviors[-(i + 1)]]

        self.create_gui_elements(config_data)
        self.gui.update_scroll_region()

    def apply_settings(self):
        params = {key: entry.get() for key, entry in self.gui.entries.items()}
        behaviors = {}
        for key, value in params.items():
            keys = key.split('.')
            behavior_name = keys[0]
            if behavior_name not in behaviors:
                behaviors[behavior_name] = {}

            section = keys[1] if len(keys) > 2 else ""
            param = keys[-1]

            if section:
                if section not in behaviors[behavior_name]:
                    behaviors[behavior_name][section] = {}
                behaviors[behavior_name][section][param] = self.convert_value(value)
            else:
                behaviors[behavior_name][param] = self.convert_value(value)

        config_data = {'behaviors': behaviors}
        self.config_generator.config = config_data

        run_name = self.gui.run_name_entry.get() or "default_run"
        if not self.config_path:
            self.config_path = os.path.join(os.getcwd(), f"{run_name}_config.yaml")
        try:
            output_file = os.path.join(os.path.dirname(self.config_path), f"{run_name}_config.yaml")
            self.config_generator.save_yaml_file(output_file)
            self.gui.update_console_output(f"Settings Applied: {params}")
            self.gui.status_label.config(text="Status: Configuration Applied")

            # Save settings to the settings file
            self.save_settings()
        except Exception as e:
            self.gui.update_console_output(f"An error occurred: {e}")
            self.gui.status_label.config(text="Status: Error")

    def save_settings(self):
        settings = {
            'conda_env_name': self.conda_env_name,
            'executable_path': self.executable_path,
            'run_name': self.gui.run_name_entry.get(),
            'no_graphics': self.gui.no_graphics_var.get(),
            'time_scale': self.gui.time_scale_var.get()
        }
        with open(self.SETTINGS_FILE, 'w') as f:
            json.dump(settings, f)

    def load_settings(self):
        if os.path.exists(self.SETTINGS_FILE):
            with open(self.SETTINGS_FILE, 'r') as f:
                settings = json.load(f)
                self.conda_env_name = settings.get('conda_env_name', self.conda_env_name)
                self.executable_path = settings.get('executable_path', self.executable_path)
                run_name = settings.get('run_name', '')
                self.gui.conda_env_entry.delete(0, tk.END)
                self.gui.conda_env_entry.insert(0, self.conda_env_name)
                self.gui.executable_entry.delete(0, tk.END)
                self.gui.executable_entry.insert(0, self.executable_path)
                self.gui.run_name_entry.delete(0, tk.END)
                self.gui.run_name_entry.insert(0, run_name)
                self.gui.no_graphics_var.set(settings.get('no_graphics', False))
                self.gui.time_scale_var.set(settings.get('time_scale', False))

    def convert_value(self, value):
        try:
            if value.lower() in ['true', 'false']:
                return value.lower() == 'true'
            elif '.' in value:
                return float(value)
            else:
                return int(value)
        except ValueError:
            try:
                return yaml.safe_load(value)
            except yaml.YAMLError:
                return value

    def delete_behavior(self, behavior_name):
        if 'behaviors' in self.config_generator.config and behavior_name in self.config_generator.config['behaviors']:
            del self.config_generator.config['behaviors'][behavior_name]
            self.create_gui_elements(self.config_generator.config)
            self.gui.update_scroll_region()

    def start_training_thread(self):
        run_name = self.gui.run_name_entry.get()
        conda_env_name = self.conda_env_name
        executable_path = self.executable_path

        if not conda_env_name:
            self.gui.update_console_output("Error: Conda environment name is not set.")
            return

        if not executable_path:
            self.gui.update_console_output("Error: Unity executable is not selected.")
            return

        no_graphics = self.gui.no_graphics_var.get()
        time_scale = self.gui.time_scale_var.get()

        self.trainer = ZTrainer(self.config_path, run_name, conda_env_name, self.mlagents_learn_path, executable_path, no_graphics, time_scale)
        self.trainer.start_training(self.gui.update_console_output)

    def start_tensorboard_thread(self):
        tensorboard_env_name = self.conda_env_name  # Use the same environment for TensorBoard
        self.tensorboard_manager = ZTensorBoardManager(tensorboard_env_name)
        self.tensorboard_manager.start_tensorboard(self.gui.update_console_output)
        self.gui.add_tensorboard_link()

    def on_closing(self):
        if self.trainer:
            self.trainer.stop()
        if self.tensorboard_manager:
            self.tensorboard_manager.stop()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = MLAgentApp(root)
    root.mainloop()
