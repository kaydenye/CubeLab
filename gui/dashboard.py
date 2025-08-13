#   Name: Kayden Ye
#   Date: 13/08/2025
#   File: gui/dashboard.py

import customtkinter as ctk
from typing import Optional, Callable
from classes.algorithm_util import AlgorithmUtil
from classes.timer_util import TimerUtil
from .components import HeaderFrame, FONT
from .algorithm_list import AlgorithmList
import tkinter as tk
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

class DashboardCard(ctk.CTkFrame):
    """Base card component for dashboard"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, fg_color="#33363D", corner_radius=15, **kwargs)

class AlgorithmCard(DashboardCard):
    """Card displaying algorithm details with cube image"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.algorithm_util = AlgorithmUtil()
        self.setup_ui()
    
    def setup_ui(self):
        """Setup algorithm card UI"""
        # Title
        self.title_label = ctk.CTkLabel(self, text="Select Algorithm", font=(FONT, 24, "bold"))
        self.title_label.pack(pady=(20, 10))
        
        # Notation
        self.notation_label = ctk.CTkLabel(self, text="Select an algorithm to view details", font=(FONT, 16), text_color="gray")
        self.notation_label.pack(pady=(0, 20))
        
        # Cube image placeholder
        cube_frame = ctk.CTkFrame(self, fg_color="transparent")
        cube_frame.pack(expand=True)
        
        # Create a simple cube representation
        cube_label = ctk.CTkLabel(cube_frame, text="🧩", font=("Arial", 80))
        cube_label.pack()
    
    def update_algorithm(self, algorithm_name: str):
        """Update card with algorithm data"""
        try:
            # Get algorithm details
            algorithm = self.algorithm_util.get_algorithm(algorithm_name)
            if algorithm:
                self.title_label.configure(text=algorithm_name)
                self.notation_label.configure(text=algorithm.notation if hasattr(algorithm, 'notation') else "No notation available")
            else:
                self.title_label.configure(text="Algorithm Not Found")
                self.notation_label.configure(text="No notation available")
        except Exception as e:
            self.title_label.configure(text="Error Loading")
            self.notation_label.configure(text="Could not load algorithm data")

class TagsCard(DashboardCard):
    """Card displaying tags"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.algorithm_util = AlgorithmUtil()
        self.setup_ui()
    
    def setup_ui(self):
        """Setup tags card UI"""
        # Tags container
        self.tags_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.tags_frame.pack(expand=True, padx=20, pady=20)
        
        # Default message
        self.default_label = ctk.CTkLabel(self.tags_frame, text="Select an algorithm to view tags", font=(FONT, 14), text_color="gray")
        self.default_label.pack(expand=True)
    
    def update_tags(self, algorithm_name: str):
        """Update card with algorithm tags"""
        # Clear existing tags
        for widget in self.tags_frame.winfo_children():
            widget.destroy()
        
        try:
            # Get algorithm details
            algorithm = self.algorithm_util.get_algorithm(algorithm_name)
            if algorithm and hasattr(algorithm, 'tags') and algorithm.tags:
                row = 0
                col = 0
                for i, tag in enumerate(algorithm.tags):
                    tag_btn = ctk.CTkButton(
                        self.tags_frame, 
                        text=tag, 
                        width=max(80, len(tag) * 10),
                        height=30,
                        font=(FONT, 12)
                    )
                    tag_btn.grid(row=row, column=col, padx=5, pady=5, sticky="w")
                    
                    col += 1
                    if col > 2:  # 3 columns max
                        col = 0
                        row += 1
            else:
                no_tags_label = ctk.CTkLabel(self.tags_frame, text="No tags available", font=(FONT, 14), text_color="gray")
                no_tags_label.pack(expand=True)
        except Exception as e:
            error_label = ctk.CTkLabel(self.tags_frame, text="Error loading tags", font=(FONT, 14), text_color="gray")
            error_label.pack(expand=True)

class BarChartCard(DashboardCard):
    """Card displaying bar chart"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.setup_ui()
    
    def setup_ui(self):
        """Setup bar chart card UI"""
        # Create matplotlib figure
        fig, ax = plt.subplots(figsize=(4, 3), facecolor='#33363D')
        ax.set_facecolor('#33363D')
        
        # Sample data
        x_labels = ['1.0', '0.9', '0.8', '0.7', '0.6', '0.5', '0.4', '0.3', '0.2']
        values = [5, 15, 65, 35, 10, 8, 6, 4, 2]
        
        # Create bars
        bars = ax.bar(range(len(values)), values, color='#4A9EFF', width=0.8)
        
        # Customize chart
        ax.set_xticks(range(len(x_labels)))
        ax.set_xticklabels(x_labels, color='gray', fontsize=8)
        ax.set_ylim(0, 80)
        ax.set_yticks(range(0, 81, 10))
        ax.set_yticklabels([str(i) for i in range(0, 81, 10)], color='gray', fontsize=8)
        ax.tick_params(colors='gray')
        
        # Remove spines
        for spine in ax.spines.values():
            spine.set_visible(False)
        
        # Grid
        ax.grid(True, alpha=0.3, color='gray')
        ax.set_axisbelow(True)
        
        # Embed in tkinter
        canvas = FigureCanvasTkAgg(fig, self)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

class TimerListCard(DashboardCard):
    """Card displaying timer list"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.timer_util = TimerUtil()
        self.setup_ui()
    
    def setup_ui(self):
        """Setup timer list card UI"""
        # Scrollable frame
        self.scrollable = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scrollable.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Default message
        self.default_label = ctk.CTkLabel(self.scrollable, text="Select an algorithm to view times", font=(FONT, 14), text_color="gray")
        self.default_label.pack(expand=True, pady=20)
    
    def update_times(self, algorithm_name: str):
        """Update card with algorithm times"""
        # Clear existing times
        for widget in self.scrollable.winfo_children():
            widget.destroy()
        
        # Get times for the algorithm
        times_data = self.timer_util.get_algorithm_times(algorithm_name)
        
        if not times_data:
            no_times_label = ctk.CTkLabel(self.scrollable, text="No times recorded yet", font=(FONT, 14), text_color="gray")
            no_times_label.pack(expand=True, pady=20)
            return
        
        # Display latest 11 times (like in the original design)
        latest_times = times_data[:11] if len(times_data) > 11 else times_data
        
        for i, (time_seconds, timestamp) in enumerate(latest_times):
            row_frame = ctk.CTkFrame(self.scrollable, fg_color="transparent")
            row_frame.pack(fill="x", pady=1)
            
            # Number
            num_label = ctk.CTkLabel(row_frame, text=f"{i+1}.", font=(FONT, 12), width=30)
            num_label.pack(side="left")
            
            # Time
            time_label = ctk.CTkLabel(row_frame, text=f"{time_seconds:.2f}", font=(FONT, 12, "bold"), width=50)
            time_label.pack(side="left")
            
            # +2 button
            plus2_btn = ctk.CTkButton(row_frame, text="+2", width=30, height=20, font=(FONT, 10))
            plus2_btn.pack(side="left", padx=2)
            
            # DNF button  
            dnf_btn = ctk.CTkButton(row_frame, text="DNF", width=30, height=20, font=(FONT, 10))
            dnf_btn.pack(side="left", padx=2)
            
            # X button
            x_btn = ctk.CTkButton(row_frame, text="✗", width=20, height=20, font=(FONT, 10))
            x_btn.pack(side="right")

class StatsCard(DashboardCard):
    """Card displaying statistics"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.timer_util = TimerUtil()
        self.setup_ui()
    
    def setup_ui(self):
        """Setup stats card UI"""
        # Main container
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.pack(expand=True, padx=20, pady=20)
        
        # Default message
        self.default_label = ctk.CTkLabel(self.main_frame, text="Select an algorithm to view statistics", font=(FONT, 14), text_color="gray")
        self.default_label.pack(expand=True)
    
    def update_stats(self, algorithm_name: str):
        """Update card with algorithm statistics"""
        # Clear existing widgets
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        
        # Get times for the algorithm
        times_data = self.timer_util.get_algorithm_times(algorithm_name)
        
        if not times_data:
            no_stats_label = ctk.CTkLabel(self.main_frame, text="No statistics available", font=(FONT, 14), text_color="gray")
            no_stats_label.pack(expand=True)
            return
        
        # Calculate statistics
        times_only = [time for time, _ in times_data]
        stats = self.timer_util.get_time_statistics(times_data)
        
        # PB and AVG row
        top_row = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        top_row.pack(fill="x", pady=(0, 20))
        
        # PB section
        pb_frame = ctk.CTkFrame(top_row, fg_color="transparent")
        pb_frame.pack(side="left", expand=True)
        
        pb_label = ctk.CTkLabel(pb_frame, text="pb", font=(FONT, 14), text_color="gray")
        pb_label.pack()
        pb_value = ctk.CTkLabel(pb_frame, text=f"{stats['best']:.2f}" if stats else "N/A", font=(FONT, 36, "bold"))
        pb_value.pack()
        
        # AVG section
        avg_frame = ctk.CTkFrame(top_row, fg_color="transparent")
        avg_frame.pack(side="right", expand=True)
        
        avg_label = ctk.CTkLabel(avg_frame, text="avg", font=(FONT, 14), text_color="gray")
        avg_label.pack()
        avg_value = ctk.CTkLabel(avg_frame, text=f"{stats['average']:.2f}" if stats else "N/A", font=(FONT, 36, "bold"))
        avg_value.pack()
        
        # Calculate ao5 and ao12
        ao5_pb = self._calculate_best_average(times_only, 5)
        ao5_current = self._calculate_current_average(times_only, 5)
        ao12_pb = self._calculate_best_average(times_only, 12)
        ao12_current = self._calculate_current_average(times_only, 12)
        
        # Bottom section
        bottom_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        bottom_frame.pack(fill="x")
        
        # ao5 pb
        ao5_pb_frame = ctk.CTkFrame(bottom_frame, fg_color="transparent")
        ao5_pb_frame.pack(side="left", expand=True)
        
        ao5_pb_label = ctk.CTkLabel(ao5_pb_frame, text="ao5 pb", font=(FONT, 12), text_color="gray")
        ao5_pb_label.pack()
        ao5_pb_value = ctk.CTkLabel(ao5_pb_frame, text=f"{ao5_pb:.2f}" if ao5_pb else "N/A", font=(FONT, 20, "bold"))
        ao5_pb_value.pack()
        
        # ao5
        ao5_frame = ctk.CTkFrame(bottom_frame, fg_color="transparent")
        ao5_frame.pack(side="right", expand=True)
        
        ao5_label = ctk.CTkLabel(ao5_frame, text="ao5", font=(FONT, 12), text_color="gray")
        ao5_label.pack()
        ao5_value = ctk.CTkLabel(ao5_frame, text=f"{ao5_current:.2f}" if ao5_current else "N/A", font=(FONT, 20, "bold"))
        ao5_value.pack()
        
        # Spacer
        spacer = ctk.CTkFrame(self.main_frame, fg_color="transparent", height=10)
        spacer.pack(fill="x")
        
        # ao12 pb  
        ao12_pb_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        ao12_pb_frame.pack(side="left", expand=True)
        
        ao12_pb_label = ctk.CTkLabel(ao12_pb_frame, text="ao12 pb", font=(FONT, 12), text_color="gray")
        ao12_pb_label.pack()
        ao12_pb_value = ctk.CTkLabel(ao12_pb_frame, text=f"{ao12_pb:.2f}" if ao12_pb else "N/A", font=(FONT, 20, "bold"))
        ao12_pb_value.pack()
        
        # ao12
        ao12_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        ao12_frame.pack(side="right", expand=True)
        
        ao12_label = ctk.CTkLabel(ao12_frame, text="ao12", font=(FONT, 12), text_color="gray")
        ao12_label.pack()
        ao12_value = ctk.CTkLabel(ao12_frame, text=f"{ao12_current:.2f}" if ao12_current else "N/A", font=(FONT, 20, "bold"))
        ao12_value.pack()
    
    def _calculate_best_average(self, times, count):
        """Calculate best average of count"""
        if len(times) < count:
            return None
        
        best_avg = float('inf')
        for i in range(len(times) - count + 1):
            window = times[i:i+count]
            # Remove best and worst for average calculation (standard cubing practice)
            if count >= 3:
                sorted_window = sorted(window)
                avg_times = sorted_window[1:-1]  # Remove best and worst
                avg = sum(avg_times) / len(avg_times)
            else:
                avg = sum(window) / len(window)
            
            if avg < best_avg:
                best_avg = avg
        
        return best_avg if best_avg != float('inf') else None
    
    def _calculate_current_average(self, times, count):
        """Calculate current average of count (most recent times)"""
        if len(times) < count:
            return None
        
        recent_times = times[:count]  # Get most recent times
        # Remove best and worst for average calculation
        if count >= 3:
            sorted_times = sorted(recent_times)
            avg_times = sorted_times[1:-1]  # Remove best and worst
            return sum(avg_times) / len(avg_times)
        else:
            return sum(recent_times) / len(recent_times)

class LineChartCard(DashboardCard):
    """Card displaying line chart"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.setup_ui()
    
    def setup_ui(self):
        """Setup line chart card UI"""
        # Create matplotlib figure
        fig, ax = plt.subplots(figsize=(4, 3), facecolor='#33363D')
        ax.set_facecolor('#33363D')
        
        # Sample data - declining trend
        x = np.linspace(0, 10, 50)
        y = 1.0 * np.exp(-x/3) + 0.2 + 0.05 * np.random.randn(50)
        
        # Create line chart
        ax.plot(x, y, color='#4A9EFF', linewidth=2)
        
        # Customize chart
        ax.set_ylim(0, 1.0)
        ax.set_xlim(0, 10)
        ax.set_yticks([0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0])
        ax.set_yticklabels(['0.1', '0.2', '0.3', '0.4', '0.5', '0.6', '0.7', '0.8', '0.9', '1.0'], 
                          color='gray', fontsize=8)
        ax.tick_params(colors='gray')
        
        # Remove spines
        for spine in ax.spines.values():
            spine.set_visible(False)
        
        # Grid
        ax.grid(True, alpha=0.3, color='gray')
        ax.set_axisbelow(True)
        
        # Remove x-axis labels
        ax.set_xticks([])
        
        # Embed in tkinter
        canvas = FigureCanvasTkAgg(fig, self)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

class Dashboard:
    """Dashboard component with card-based layout"""
    
    def __init__(self, parent_frame: ctk.CTkFrame, on_back: Callable = None):
        self.parent_frame = parent_frame
        self.on_back = on_back
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup dashboard UI"""
        # Configure grid
        self.parent_frame.grid_rowconfigure(0, weight=0)  # header
        self.parent_frame.grid_rowconfigure(1, weight=1)  # content
        self.parent_frame.grid_columnconfigure(0, weight=1)
        
        # Header
        self.header = HeaderFrame(
            self.parent_frame,
            show_back=True,
            on_back=self.on_back,
            on_exit=self.exit_app
        )
        self.header.grid(row=0, column=0, sticky="ew")
        
        # Main content frame
        main_content = ctk.CTkFrame(self.parent_frame, fg_color="#222326")
        main_content.grid(row=1, column=0, sticky="nsew")
        main_content.grid_columnconfigure(0, weight=1)  # dashboard cards
        main_content.grid_columnconfigure(1, weight=0)  # algorithm list
        main_content.grid_rowconfigure(0, weight=1)
        
        # Dashboard cards frame (left side)
        self.content_frame = ctk.CTkFrame(main_content, fg_color="#222326")
        self.content_frame.grid(row=0, column=0, sticky="nsew")
        
        # Configure grid for 3x2 layout
        for i in range(3):
            self.content_frame.grid_columnconfigure(i, weight=1)
        for i in range(2):
            self.content_frame.grid_rowconfigure(i, weight=1)
        
        # Create cards
        # Top row
        self.algorithm_card = AlgorithmCard(self.content_frame)
        self.algorithm_card.grid(row=0, column=0, sticky="nsew", padx=(15, 7.5), pady=(15, 7.5))
        
        self.tags_card = TagsCard(self.content_frame)
        self.tags_card.grid(row=0, column=1, sticky="nsew", padx=(7.5, 7.5), pady=(15, 7.5))
        
        self.bar_chart_card = BarChartCard(self.content_frame)
        self.bar_chart_card.grid(row=0, column=2, sticky="nsew", padx=(7.5, 7.5), pady=(15, 7.5))
        
        # Bottom row
        self.timer_list_card = TimerListCard(self.content_frame)
        self.timer_list_card.grid(row=1, column=0, sticky="nsew", padx=(15, 7.5), pady=(7.5, 15))
        
        self.stats_card = StatsCard(self.content_frame)
        self.stats_card.grid(row=1, column=1, sticky="nsew", padx=(7.5, 7.5), pady=(7.5, 15))
        
        self.line_chart_card = LineChartCard(self.content_frame)
        self.line_chart_card.grid(row=1, column=2, sticky="nsew", padx=(7.5, 15), pady=(7.5, 15))
        
        # Algorithm list (right side)
        self.algorithm_list = AlgorithmList(
            main_content,
            on_algorithm_select=self.on_algorithm_select,
            show_remove=False,  # Don't show remove on dashboard
            show_add=False,     # Don't show add on dashboard
            show_count=True     # Show time counts
        )
        self.algorithm_list.grid(row=0, column=1, sticky="nsew")
    
    def on_algorithm_select(self, algorithm_name: str):
        """Handle algorithm selection"""
        # Update all cards with data for the selected algorithm
        self.algorithm_card.update_algorithm(algorithm_name)
        self.tags_card.update_tags(algorithm_name)
        self.timer_list_card.update_times(algorithm_name)
        self.stats_card.update_stats(algorithm_name)
        # Bar chart and line chart updates can be added later if needed
    
    def exit_app(self):
        """Exit the application"""
        self.parent_frame.winfo_toplevel().destroy()
