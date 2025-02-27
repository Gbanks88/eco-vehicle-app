import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from api.integration_api import IntegrationAPI

class UnifiedLauncher:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Eco Vehicle Project - Unified Launcher")
        self.root.geometry("800x600")
        
        self.api = IntegrationAPI()
        
        self.setup_ui()
        
    def setup_ui(self):
        # Create notebook for tabs
        notebook = ttk.Notebook(self.root)
        notebook.pack(expand=True, fill='both', padx=10, pady=10)
        
        # SysML Model Tab
        sysml_frame = ttk.Frame(notebook)
        notebook.add(sysml_frame, text='SysML Model')
        self.setup_sysml_tab(sysml_frame)
        
        # Game Tab
        game_frame = ttk.Frame(notebook)
        notebook.add(game_frame, text='Recycle Quest Game')
        self.setup_game_tab(game_frame)
        
        # Fusion 360 Tab
        fusion_frame = ttk.Frame(notebook)
        notebook.add(fusion_frame, text='Fusion 360 Model')
        self.setup_fusion_tab(fusion_frame)
        
        # Integration Controls
        control_frame = ttk.LabelFrame(self.root, text='Integration Controls')
        control_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Button(control_frame, text='Sync All Systems', 
                  command=self.sync_systems).pack(side='left', padx=5, pady=5)
        ttk.Button(control_frame, text='Export All', 
                  command=self.export_all).pack(side='left', padx=5, pady=5)
        ttk.Button(control_frame, text='System Status', 
                  command=self.show_status).pack(side='left', padx=5, pady=5)

    def setup_sysml_tab(self, parent):
        # Diagram Type Selection
        diagram_frame = ttk.LabelFrame(parent, text='Generate Diagrams')
        diagram_frame.pack(fill='x', padx=10, pady=5)
        
        diagram_types = ['bdd', 'ibd', 'pkg', 'req', 'sd', 'stm', 'uc']
        self.diagram_var = tk.StringVar(value='bdd')
        
        for d_type in diagram_types:
            ttk.Radiobutton(diagram_frame, text=d_type.upper(), 
                          variable=self.diagram_var, 
                          value=d_type).pack(side='left', padx=5)
        
        ttk.Button(diagram_frame, text='Generate Diagram', 
                  command=self.generate_diagram).pack(side='right', padx=5)

    def setup_game_tab(self, parent):
        # Game Controls
        game_frame = ttk.LabelFrame(parent, text='Game Controls')
        game_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Button(game_frame, text='Start New Game', 
                  command=self.start_game).pack(side='left', padx=5, pady=5)
        ttk.Button(game_frame, text='Load Game', 
                  command=self.load_game).pack(side='left', padx=5, pady=5)
        ttk.Button(game_frame, text='View Stats', 
                  command=self.view_game_stats).pack(side='left', padx=5, pady=5)

    def setup_fusion_tab(self, parent):
        # Fusion 360 Controls
        fusion_frame = ttk.LabelFrame(parent, text='Fusion 360 Controls')
        fusion_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Button(fusion_frame, text='Update Model', 
                  command=self.update_fusion_model).pack(side='left', padx=5, pady=5)
        ttk.Button(fusion_frame, text='Export Model', 
                  command=self.export_fusion_model).pack(side='left', padx=5, pady=5)
        ttk.Button(fusion_frame, text='View Model', 
                  command=self.view_fusion_model).pack(side='left', padx=5, pady=5)

    def generate_diagram(self):
        try:
            diagram_type = self.diagram_var.get()
            self.api.generate_sysml_diagrams(diagram_type)
            messagebox.showinfo("Success", f"Generated {diagram_type.upper()} diagram")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate diagram: {str(e)}")

    def start_game(self):
        try:
            self.api.game_state.initialize_game("Player1")
            messagebox.showinfo("Success", "Game started successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start game: {str(e)}")

    def load_game(self):
        messagebox.showinfo("Info", "Game loading feature coming soon...")

    def view_game_stats(self):
        stats = self.api.game_state.get_stats()
        messagebox.showinfo("Game Stats", 
                          f"Score: {stats['score']}\n"
                          f"Level: {stats['level']}\n"
                          f"Items Recycled: {stats['total_items_recycled']}\n"
                          f"Energy Saved: {stats['total_energy_saved']:.2f} kWh\n"
                          f"CO2 Reduced: {stats['total_co2_reduced']:.2f} kg")

    def update_fusion_model(self):
        try:
            config = self.api.load_vehicle_config()
            self.api.update_fusion360_model(config)
            messagebox.showinfo("Success", "Fusion 360 model updated")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update model: {str(e)}")

    def export_fusion_model(self):
        try:
            export_path = os.path.join(os.path.dirname(__file__), 
                                     '../exports/eco_vehicle.f3d')
            self.api.export_fusion360_model(export_path)
            messagebox.showinfo("Success", f"Model exported to {export_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export model: {str(e)}")

    def view_fusion_model(self):
        messagebox.showinfo("Info", "Opening Fusion 360...")

    def sync_systems(self):
        try:
            result = self.api.sync_all_systems()
            messagebox.showinfo("Success", "All systems synchronized successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Sync failed: {str(e)}")

    def export_all(self):
        try:
            # Export diagrams
            self.api.generate_sysml_diagrams("all")
            
            # Export Fusion 360 model
            export_path = os.path.join(os.path.dirname(__file__), 
                                     '../exports/eco_vehicle.f3d')
            self.api.export_fusion360_model(export_path)
            
            # Export game state
            game_stats = self.api.game_state.get_stats()
            with open('../exports/game_state.json', 'w') as f:
                json.dump(game_stats, f, indent=2)
                
            messagebox.showinfo("Success", "All systems exported successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Export failed: {str(e)}")

    def show_status(self):
        status = self.api.get_system_status()
        status_text = "System Status:\n\n"
        for system, info in status.items():
            status_text += f"{system.upper()}:\n"
            for key, value in info.items():
                status_text += f"  {key}: {value}\n"
            status_text += "\n"
        messagebox.showinfo("System Status", status_text)

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    launcher = UnifiedLauncher()
    launcher.run()
