#   Name: Kayden Ye
#   Date: 13/08/2025
#   File: gui/dashboard.py

import customtkinter as ctk
from typing import Optional, Callable
from classes.algorithm import Algorithm
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
        # Ensure the card doesn't expand beyond its set size
        self.grid_propagate(False)
        self.pack_propagate(False)

class AlgorithmCard(DashboardCard):
    """Card displaying algorithm details with cube image"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.algorithm = Algorithm()
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

    def update_algorithm(self, algorithm_name: str):
        """Update card with algorithm data"""
        try:
            details = self.algorithm.get_algorithm_details(algorithm_name)
            if details:
                notation, tags = details
                self.title_label.configure(text=algorithm_name)
                self.notation_label.configure(text=notation)
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
        self.algorithm = Algorithm()
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
            details = self.algorithm.get_algorithm_details(algorithm_name)
            if details:
                notation, tags = details
                if tags:
                    row = 0
                    col = 0
                    for i, tag in enumerate(tags):
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
            else:
                error_label = ctk.CTkLabel(self.tags_frame, text="Algorithm not found", font=(FONT, 14), text_color="gray")
                error_label.pack(expand=True)
        except Exception as e:
            error_label = ctk.CTkLabel(self.tags_frame, text="Error loading tags", font=(FONT, 14), text_color="gray")
            error_label.pack(expand=True)

class BarChartCard(DashboardCard):
    """Card displaying bar chart"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.timer_util = TimerUtil()
        self.canvas = None
        self.fig = None
        self.ax = None
        self._resize_after_id = None
        self._resize_bound = False
        self.setup_ui()
    
    def setup_ui(self):
        """Setup bar chart card UI"""
        self.create_chart([])
        self._bind_resize()
    
    def create_chart(self, times_data):
        """Create or update the bar chart"""
        # Clear existing chart widget
        for widget in self.winfo_children():
            widget.destroy()
        # Close existing fig if any
        try:
            if self.fig is not None:
                plt.close(self.fig)
        except Exception:
            pass
        
        # Create matplotlib figure
        fig, ax = plt.subplots(figsize=(3, 2.5), facecolor='#33363D', constrained_layout=True)
        fig.set_dpi(100)
        ax.set_facecolor('#33363D')
        self.fig, self.ax = fig, ax
        
        if times_data:
            # Create histogram of times
            times = [float(t[0]) for t in times_data]
            bins = 10
            counts, bin_edges = np.histogram(times, bins=bins)
            bin_centers = [(bin_edges[i] + bin_edges[i+1]) / 2 for i in range(len(bin_edges) - 1)]
            
            # Create bars
            ax.bar(range(len(counts)), counts, color='#4A9EFF', width=0.8)
            
            # Customize chart
            ax.set_xticks(range(len(bin_centers)))
            # Downsample tick labels if too many
            labels = [f'{x:.1f}' for x in bin_centers]
            if len(labels) > 10:
                step = max(1, len(labels) // 10)
                ax.set_xticks(list(range(0, len(labels), step)))
                labels = labels[::step]
            ax.set_xticklabels(labels, color='gray', fontsize=8, rotation=45)
            ax.set_ylabel('Count', color='gray', fontsize=8)
        else:
            # Show empty state
            ax.text(0.5, 0.5, 'No Data', transform=ax.transAxes,
                    ha='center', va='center', color='gray', fontsize=12)
        
        ax.tick_params(colors='gray')
        
        # Remove spines
        for spine in ax.spines.values():
            spine.set_visible(False)
        
        # Grid
        ax.grid(True, alpha=0.3, color='gray')
        ax.set_axisbelow(True)
        
        # Embed in tkinter
        self.canvas = FigureCanvasTkAgg(fig, self)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
        # Ensure initial sizing fits the container
        self._schedule_resize()

    def _bind_resize(self):
        """Bind resize events for responsive matplotlib sizing"""
        if not self._resize_bound:
            self.bind("<Configure>", lambda e: self._schedule_resize())
            self._resize_bound = True

    def _schedule_resize(self):
        """Debounce resize to avoid excessive redraws"""
        if self._resize_after_id:
            try:
                self.after_cancel(self._resize_after_id)
            except Exception:
                pass
        self._resize_after_id = self.after(100, self._on_resize)

    def _on_resize(self):
        if not self.canvas or not self.fig:
            return
        # Compute available inner size (account for padding used in pack)
        width = max(50, self.winfo_width() - 20)
        height = max(50, self.winfo_height() - 20)
        try:
            dpi = self.fig.get_dpi() or 100
            self.fig.set_size_inches(width / dpi, height / dpi, forward=True)
            # Let constrained layout handle the axes area
            if hasattr(self.fig, "set_layout_engine"):
                try:
                    self.fig.set_layout_engine("constrained")
                except Exception:
                    pass
            self.canvas.get_tk_widget().configure(width=width, height=height)
            self.canvas.draw_idle()
        except Exception:
            # Fallback: force a draw
            self.canvas.draw()
    
    def destroy(self):
        """Clean up matplotlib resources"""
        try:
            if hasattr(self, 'canvas') and self.canvas:
                self.canvas.get_tk_widget().destroy()
                self.canvas = None
            self.fig = None
            self.ax = None
            plt.close('all')
        except:
            pass
        super().destroy()
    
    def update_algorithm(self, algorithm_name: str):
        """Update chart with algorithm times"""
        try:
            times_data = self.timer_util.get_algorithm_times(algorithm_name)
            self.create_chart(times_data)
        except Exception as e:
            self.create_chart([])

class TimerListCard(DashboardCard):
    """Card displaying timer list"""
    
    def __init__(self, parent, dashboard=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.timer_util = TimerUtil()
        self.dashboard = dashboard
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
        
        # Get times for the algorithm with IDs and penalty flags
        times_data = self.timer_util.get_algorithm_times_with_ids(algorithm_name)
        
        if not times_data:
            no_times_label = ctk.CTkLabel(self.scrollable, text="No times recorded yet", font=(FONT, 14), text_color="gray")
            no_times_label.pack(expand=True, pady=20)
            return
        
        total_times = len(times_data)
        
        for i, (time_id, time_seconds, timestamp, plus_two, dnf) in enumerate(times_data):
            row_frame = ctk.CTkFrame(self.scrollable, fg_color="transparent")
            row_frame.pack(fill="x", pady=1)
            
            # Number (descending order)
            solve_number = total_times - i
            num_label = ctk.CTkLabel(row_frame, text=f"{solve_number}.", font=(FONT, 12), width=40)
            num_label.pack(side="left")
            
            # Calculate display time (add 2 seconds if plus_two is True)
            display_time = time_seconds + (2.0 if plus_two else 0.0)
            
            # Time label with conditional formatting
            if dnf:
                time_text = "DNF"
                time_color = "red"
            else:
                time_text = f"{display_time:.2f}" + (" (+2)" if plus_two else "")
                time_color = "orange" if plus_two else "white"
            
            time_label = ctk.CTkLabel(row_frame, text=time_text, font=(FONT, 12, "bold"), 
                                    width=80, text_color=time_color)
            time_label.pack(side="left", padx=(5, 0))
            
            # +2 button (disabled if already applied or DNF)
            plus2_state = "disabled" if plus_two or dnf else "normal"
            plus2_color = "gray" if plus_two or dnf else None
            plus2_btn = ctk.CTkButton(
                row_frame, text="+2", width=30, height=20, font=(FONT, 10),
                state=plus2_state, fg_color=plus2_color,
                command=lambda tid=time_id, alg=algorithm_name: self.apply_plus_two(tid, alg),
                hover=False  # Disable hover animation for faster response
            )
            plus2_btn.pack(side="left", padx=2)
            
            # DNF button (toggle)
            dnf_color = "red" if dnf else None
            dnf_btn = ctk.CTkButton(
                row_frame, text="DNF", width=30, height=20, font=(FONT, 10),
                fg_color=dnf_color,
                command=lambda tid=time_id, alg=algorithm_name, is_dnf=dnf: self.toggle_dnf(tid, alg, is_dnf),
                hover=False  # Disable hover animation for faster response
            )
            dnf_btn.pack(side="left", padx=2)
            
            # X button (delete)
            x_btn = ctk.CTkButton(
                row_frame, text="X", width=20, height=20, font=(FONT, 10),
                fg_color="red", hover_color="darkred",
                command=lambda tid=time_id, alg=algorithm_name: self.delete_time(tid, alg),
                hover=False  # Disable hover animation for faster response
            )
            x_btn.pack(side="right")
    
    def apply_plus_two(self, time_id: int, algorithm_name: str):
        """Apply +2 penalty to a time"""
        if self.timer_util.update_time_penalty(time_id, plus_two=True):
            self.update_times(algorithm_name)  # Refresh the display
            # Update other dashboard cards
            if self.dashboard:
                self.dashboard.on_algorithm_select(algorithm_name)
    
    def toggle_dnf(self, time_id: int, algorithm_name: str, current_dnf: bool):
        """Toggle DNF status for a time"""
        new_dnf = not current_dnf
        # If setting DNF, remove +2 penalty
        if new_dnf:
            self.timer_util.update_time_penalty(time_id, plus_two=False, dnf=True)
        else:
            self.timer_util.update_time_penalty(time_id, dnf=False)
        
        self.update_times(algorithm_name)  # Refresh the display
        # Update other dashboard cards
        if self.dashboard:
            self.dashboard.on_algorithm_select(algorithm_name)
    
    def delete_time(self, time_id: int, algorithm_name: str):
        """Delete a time from the database"""
        if self.timer_util.delete_time(time_id):
            self.update_times(algorithm_name)  # Refresh the display
            # Update other dashboard cards
            if self.dashboard:
                self.dashboard.on_algorithm_select(algorithm_name)

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
        
        # Darker background color (10% darker than #33363D)
        darker_bg = "#2D2F35"
        
        # PB and AVG row
        top_row = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        top_row.pack(fill="x", pady=(0, 15))
        
        # PB section
        pb_frame = ctk.CTkFrame(top_row, fg_color=darker_bg, corner_radius=8)
        pb_frame.pack(side="left", expand=True, fill="both", padx=(0, 2))
        
        pb_label = ctk.CTkLabel(pb_frame, text="pb", font=(FONT, 14), text_color="gray")
        pb_label.pack(pady=(15, 0))
        pb_value = ctk.CTkLabel(pb_frame, text=f"{stats['best']:.2f}" if stats else "N/A", font=(FONT, 36, "bold"))
        pb_value.pack(pady=(0, 15))
        
        # Average section
        avg_frame = ctk.CTkFrame(top_row, fg_color=darker_bg, corner_radius=8)
        avg_frame.pack(side="right", expand=True, fill="both", padx=(2, 0))
        
        avg_label = ctk.CTkLabel(avg_frame, text="avg", font=(FONT, 14), text_color="gray")
        avg_label.pack(pady=(15, 0))
        avg_value = ctk.CTkLabel(avg_frame, text=f"{stats['average']:.2f}" if stats else "N/A", font=(FONT, 36, "bold"))
        avg_value.pack(pady=(0, 15))
        
        # Calculate ao5 and ao12
        ao5_pb = self._calculate_best_average(times_only, 5)
        ao5_current = self._calculate_current_average(times_only, 5)
        ao12_pb = self._calculate_best_average(times_only, 12)
        ao12_current = self._calculate_current_average(times_only, 12)
        
        # Bottom section
        bottom_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        bottom_frame.pack(fill="x", pady=(5, 0))
        
        # ao5 pb
        ao5_pb_frame = ctk.CTkFrame(bottom_frame, fg_color=darker_bg, corner_radius=8)
        ao5_pb_frame.pack(side="left", expand=True, fill="both", padx=(0, 2))
        
        ao5_pb_label = ctk.CTkLabel(ao5_pb_frame, text="ao5 pb", font=(FONT, 12), text_color="gray")
        ao5_pb_label.pack(pady=(12, 0))
        ao5_pb_value = ctk.CTkLabel(ao5_pb_frame, text=f"{ao5_pb:.2f}" if ao5_pb else "N/A", font=(FONT, 20, "bold"))
        ao5_pb_value.pack(pady=(0, 12))
        
        # ao5
        ao5_frame = ctk.CTkFrame(bottom_frame, fg_color=darker_bg, corner_radius=8)
        ao5_frame.pack(side="right", expand=True, fill="both", padx=(2, 0))
        
        ao5_label = ctk.CTkLabel(ao5_frame, text="ao5", font=(FONT, 12), text_color="gray")
        ao5_label.pack(pady=(12, 0))
        ao5_value = ctk.CTkLabel(ao5_frame, text=f"{ao5_current:.2f}" if ao5_current else "N/A", font=(FONT, 20, "bold"))
        ao5_value.pack(pady=(0, 12))
        
        # Spacer
        spacer = ctk.CTkFrame(self.main_frame, fg_color="transparent", height=5)
        spacer.pack(fill="x")
        
        # ao12 row
        ao12_row = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        ao12_row.pack(fill="x")
        
        # ao12 pb  
        ao12_pb_frame = ctk.CTkFrame(ao12_row, fg_color=darker_bg, corner_radius=8)
        ao12_pb_frame.pack(side="left", expand=True, fill="both", padx=(0, 2))
        
        ao12_pb_label = ctk.CTkLabel(ao12_pb_frame, text="ao12 pb", font=(FONT, 12), text_color="gray")
        ao12_pb_label.pack(pady=(12, 0))
        ao12_pb_value = ctk.CTkLabel(ao12_pb_frame, text=f"{ao12_pb:.2f}" if ao12_pb else "N/A", font=(FONT, 20, "bold"))
        ao12_pb_value.pack(pady=(0, 12))
        
        # ao12
        ao12_frame = ctk.CTkFrame(ao12_row, fg_color=darker_bg, corner_radius=8)
        ao12_frame.pack(side="right", expand=True, fill="both", padx=(2, 0))
        
        ao12_label = ctk.CTkLabel(ao12_frame, text="ao12", font=(FONT, 12), text_color="gray")
        ao12_label.pack(pady=(12, 0))
        ao12_value = ctk.CTkLabel(ao12_frame, text=f"{ao12_current:.2f}" if ao12_current else "N/A", font=(FONT, 20, "bold"))
        ao12_value.pack(pady=(0, 12))
    
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
        self.timer_util = TimerUtil()
        self.canvas = None
        self.fig = None
        self.ax = None
        self._resize_after_id = None
        self._resize_bound = False
        self.setup_ui()

    def setup_ui(self):
        """Setup line chart card UI"""
        self.create_chart([])
        self._bind_resize()

    def create_chart(self, times_data):
        """Create or update the line chart"""
        # Clear existing chart widget
        for widget in self.winfo_children():
            widget.destroy()
        # Close existing fig if any
        try:
            if self.fig is not None:
                plt.close(self.fig)
        except Exception:
            pass

        # Create matplotlib figure
        fig, ax = plt.subplots(figsize=(3, 2.5), facecolor='#33363D', constrained_layout=True)
        fig.set_dpi(100)
        ax.set_facecolor('#33363D')
        self.fig, self.ax = fig, ax

        if times_data and len(times_data) > 1:
            # Get times in chronological order
            times = [float(t[0]) for t in reversed(times_data)]
            x = range(len(times))

            # Create line chart
            ax.plot(x, times, color='#4A9EFF', linewidth=2, marker='o', markersize=3)

            # Customize chart
            ax.set_ylabel('Time (s)', color='gray', fontsize=8)
            ax.set_xlabel('Attempt', color='gray', fontsize=8)
            ax.tick_params(colors='gray')

            # Set reasonable y-limits
            min_time, max_time = min(times), max(times)
            padding = (max_time - min_time) * 0.1 if max_time > min_time else 1
            ax.set_ylim(max(0, min_time - padding), max_time + padding)
        else:
            # Show empty state
            ax.text(0.5, 0.5, 'No Data', transform=ax.transAxes,
                    ha='center', va='center', color='gray', fontsize=12)

        # Remove spines
        for spine in ax.spines.values():
            spine.set_visible(False)

        # Grid
        ax.grid(True, alpha=0.3, color='gray')
        ax.set_axisbelow(True)

        # Embed in tkinter
        self.canvas = FigureCanvasTkAgg(fig, self)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
        # Ensure initial sizing fits the container
        self._schedule_resize()

    def _bind_resize(self):
        """Bind resize events for responsive matplotlib sizing"""
        if not self._resize_bound:
            self.bind("<Configure>", lambda e: self._schedule_resize())
            self._resize_bound = True

    def _schedule_resize(self):
        """Debounce resize to avoid excessive redraws"""
        if self._resize_after_id:
            try:
                self.after_cancel(self._resize_after_id)
            except Exception:
                pass
        self._resize_after_id = self.after(100, self._on_resize)

    def _on_resize(self):
        if not self.canvas or not self.fig:
            return
        width = max(50, self.winfo_width() - 20)
        height = max(50, self.winfo_height() - 20)
        try:
            dpi = self.fig.get_dpi() or 100
            self.fig.set_size_inches(width / dpi, height / dpi, forward=True)
            if hasattr(self.fig, "set_layout_engine"):
                try:
                    self.fig.set_layout_engine("constrained")
                except Exception:
                    pass
            self.canvas.get_tk_widget().configure(width=width, height=height)
            self.canvas.draw_idle()
        except Exception:
            self.canvas.draw()

    def destroy(self):
        """Clean up matplotlib resources"""
        try:
            if hasattr(self, 'canvas') and self.canvas:
                self.canvas.get_tk_widget().destroy()
                self.canvas = None
            self.fig = None
            self.ax = None
            plt.close('all')
        except Exception:
            pass
        super().destroy()

    def update_algorithm(self, algorithm_name: str):
        """Update chart with algorithm times"""
        try:
            times_data = self.timer_util.get_algorithm_times(algorithm_name)
            self.create_chart(times_data)
        except Exception:
            self.create_chart([])

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
        main_content.grid_columnconfigure(0, weight=1)  # dashboard area
        main_content.grid_columnconfigure(1, weight=0)  # algorithm list (fixed width)
        main_content.grid_rowconfigure(0, weight=1)  # top half (empty space)
        main_content.grid_rowconfigure(1, weight=1)  # bottom half (dashboard cards)
        
        # Empty top half for spacing
        top_spacer = ctk.CTkFrame(main_content, fg_color="#222326")
        top_spacer.grid(row=0, column=0, sticky="nsew")
        
        # Dashboard cards frame (bottom half of left side)
        self.content_frame = ctk.CTkFrame(main_content, fg_color="#222326")
        self.content_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 10))
        
        # Configure grid for 3x2 layout - remove uniform to allow natural sizing
        for i in range(3):
            self.content_frame.grid_columnconfigure(i, weight=1)
        for i in range(2):
            self.content_frame.grid_rowconfigure(i, weight=1)
        
        # Create cards with square aspect ratio (fixed size)
        card_size = 400  # Increased square size for even bigger cards
        
        # Top row
        self.algorithm_card = AlgorithmCard(self.content_frame, width=card_size, height=card_size)
        self.algorithm_card.grid(row=0, column=0, padx=(15, 7.5), pady=(15, 7.5))
        
        self.tags_card = TagsCard(self.content_frame, width=card_size, height=card_size)
        self.tags_card.grid(row=0, column=1, padx=(7.5, 7.5), pady=(15, 7.5))
        
        self.bar_chart_card = BarChartCard(self.content_frame, width=card_size, height=card_size)
        self.bar_chart_card.grid(row=0, column=2, padx=(7.5, 7.5), pady=(15, 7.5))
        
        # Bottom row
        self.timer_list_card = TimerListCard(self.content_frame, dashboard=self, width=card_size, height=card_size)
        self.timer_list_card.grid(row=1, column=0, padx=(15, 7.5), pady=(7.5, 15))
        
        self.stats_card = StatsCard(self.content_frame, width=card_size, height=card_size)
        self.stats_card.grid(row=1, column=1, padx=(7.5, 7.5), pady=(7.5, 15))
        
        self.line_chart_card = LineChartCard(self.content_frame, width=card_size, height=card_size)
        self.line_chart_card.grid(row=1, column=2, padx=(7.5, 7.5), pady=(7.5, 15))
        
        # Algorithm list (right side) - spans both rows
        self.algorithm_list = AlgorithmList(
            main_content,
            on_algorithm_select=self.on_algorithm_select,
            show_remove=False,  # Don't show remove on dashboard
            show_add=False,     # Don't show add on dashboard
            show_count=True     # Show time counts
        )
        self.algorithm_list.grid(row=0, column=1, rowspan=2, sticky="nsew")
    
    def on_algorithm_select(self, algorithm_name: str):
        """Handle algorithm selection"""
        # Update all cards with data for the selected algorithm
        self.algorithm_card.update_algorithm(algorithm_name)
        self.tags_card.update_tags(algorithm_name)
        self.timer_list_card.update_times(algorithm_name)
        self.stats_card.update_stats(algorithm_name)
        self.bar_chart_card.update_algorithm(algorithm_name)
        self.line_chart_card.update_algorithm(algorithm_name)
    
    def exit_app(self):
        """Properly exit the application with cleanup"""
        try:
            # Clean up matplotlib figures
            import matplotlib.pyplot as plt
            plt.close('all')
            
            # Clean up canvas references
            if hasattr(self.bar_chart_card, 'canvas') and self.bar_chart_card.canvas:
                self.bar_chart_card.canvas.get_tk_widget().destroy()
            if hasattr(self.line_chart_card, 'canvas') and self.line_chart_card.canvas:
                self.line_chart_card.canvas.get_tk_widget().destroy()
                
        except Exception as e:
            print(f"Error during dashboard cleanup: {e}")
        finally:
            # Exit the application
            self.parent_frame.winfo_toplevel().destroy()
