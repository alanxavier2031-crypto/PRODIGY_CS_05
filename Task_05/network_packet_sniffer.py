import tkinter as tk
from tkinter import scrolledtext, messagebox, ttk
import threading
import queue
from datetime import datetime
import sys
import os

# Try to import scapy
try:
    from scapy.all import sniff, IP, TCP, UDP, ICMP, ARP, Raw, Ether, conf
    from scapy.arch import get_if_list
    SCAPY_AVAILABLE = True
except ImportError as e:
    SCAPY_AVAILABLE = False
    SCAPY_ERROR = str(e)

class PacketAnalyzerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Network Packet Analyzer - ProDigy Infotech")
        self.root.geometry("1200x700")
        
        # Application state
        self.is_sniffing = False
        self.sniffer_thread = None
        self.packet_queue = queue.Queue()
        self.packet_count = 0
        self.stored_packets = {}
        self.protocol_stats = {"TCP": 0, "UDP": 0, "ICMP": 0, "ARP": 0, "DNS": 0, "OTHER": 0}
        
        # Check scapy availability first
        if not SCAPY_AVAILABLE:
            self.show_scapy_error()
            return
        
        # Setup GUI
        self.setup_main_gui()
        
        # Start queue processing
        self.process_packet_queue()
        
        # Auto-detect and populate interfaces
        self.populate_interfaces()
    
    def show_scapy_error(self):
        """Show error if scapy is not installed"""
        error_frame = tk.Frame(self.root)
        error_frame.pack(fill="both", expand=True)
        
        error_label = tk.Label(
            error_frame,
            text="Scapy Not Installed",
            font=("Arial", 18, "bold"),
            fg="red"
        )
        error_label.pack(pady=50)
        
        error_text = f"""
Scapy library is required for packet capture.

Error: {SCAPY_ERROR}

Installation Instructions:

Windows:
  pip install scapy
  Also install Npcap from: https://npcap.com

Linux/Mac:
  sudo pip install scapy
  sudo apt-get install python3-scapy  (Ubuntu/Debian)

After installation, restart the application.
        """
        
        text_area = scrolledtext.ScrolledText(error_frame, height=15, width=70)
        text_area.pack(pady=20)
        text_area.insert("1.0", error_text)
        text_area.config(state="disabled")
        
        close_btn = tk.Button(error_frame, text="Exit", command=self.root.quit, bg="red", fg="white")
        close_btn.pack(pady=10)
    
    def setup_main_gui(self):
        """Setup the main GUI interface"""
        
        # Create menu bar
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="How to Use", command=self.show_help)
        help_menu.add_command(label="About", command=self.show_about)
        
        # Main container
        main_frame = tk.Frame(self.root, bg='#2b2b2b')
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Title
        title_label = tk.Label(
            main_frame,
            text="Network Packet Analyzer - Real-Time Traffic Monitor",
            font=("Arial", 16, "bold"),
            fg="#00ff00",
            bg='#2b2b2b'
        )
        title_label.pack(pady=10)
        
        # Warning label
        warning_label = tk.Label(
            main_frame,
            text="⚠️ FOR EDUCATIONAL USE ONLY - Capture only on networks you own or have permission ⚠️",
            font=("Arial", 9, "bold"),
            fg="yellow",
            bg='#2b2b2b'
        )
        warning_label.pack(pady=5)
        
        # Control Panel
        control_frame = tk.LabelFrame(
            main_frame, 
            text="Capture Controls", 
            bg='#3c3c3c', 
            fg="white", 
            font=("Arial", 10, "bold")
        )
        control_frame.pack(fill="x", padx=10, pady=10)
        
        # Row 0: Interface selection
        tk.Label(control_frame, text="Network Interface:", bg='#3c3c3c', fg="white").grid(
            row=0, column=0, padx=10, pady=10, sticky="w"
        )
        
        self.interface_var = tk.StringVar()
        self.interface_combo = ttk.Combobox(control_frame, textvariable=self.interface_var, width=25)
        self.interface_combo.grid(row=0, column=1, padx=10, pady=10)
        
        refresh_btn = tk.Button(
            control_frame,
            text="🔄 Refresh",
            command=self.populate_interfaces,
            bg="blue",
            fg="white"
        )
        refresh_btn.grid(row=0, column=2, padx=5, pady=10)
        
        # Row 1: Filter
        tk.Label(control_frame, text="BPF Filter:", bg='#3c3c3c', fg="white").grid(
            row=1, column=0, padx=10, pady=10, sticky="w"
        )
        
        self.filter_var = tk.StringVar()
        self.filter_entry = tk.Entry(control_frame, textvariable=self.filter_var, width=40, bg='#555', fg="white")
        self.filter_entry.grid(row=1, column=1, columnspan=2, padx=10, pady=10, sticky="w")
        
        # Filter examples
        filter_frame = tk.Frame(control_frame, bg='#3c3c3c')
        filter_frame.grid(row=1, column=3, padx=10, pady=10)
        
        tk.Label(filter_frame, text="Quick Filters:", bg='#3c3c3c', fg="white").pack(side="left")
        
        filters = ["tcp", "udp", "icmp", "arp", "port 80", "port 443"]
        for f in filters:
            btn = tk.Button(
                filter_frame,
                text=f,
                command=lambda x=f: self.filter_var.set(x),
                bg="gray",
                fg="white",
                font=("Arial", 8)
            )
            btn.pack(side="left", padx=2)
        
        # Row 2: Packet limit and buttons
        tk.Label(control_frame, text="Packet Limit:", bg='#3c3c3c', fg="white").grid(
            row=2, column=0, padx=10, pady=10, sticky="w"
        )
        
        self.count_var = tk.StringVar(value="50")
        self.count_entry = tk.Entry(control_frame, textvariable=self.count_var, width=10, bg='#555', fg="white")
        self.count_entry.grid(row=2, column=1, padx=10, pady=10, sticky="w")
        
        tk.Label(control_frame, text="(0 = unlimited)", bg='#3c3c3c', fg="gray").grid(
            row=2, column=2, padx=5, pady=10, sticky="w"
        )
        
        # Buttons
        button_frame = tk.Frame(control_frame, bg='#3c3c3c')
        button_frame.grid(row=2, column=3, padx=20, pady=10)
        
        self.start_btn = tk.Button(
            button_frame,
            text="▶ START CAPTURE",
            command=self.start_capture,
            bg="green",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=15,
            pady=5
        )
        self.start_btn.pack(side="left", padx=5)
        
        self.stop_btn = tk.Button(
            button_frame,
            text="⏹ STOP CAPTURE",
            command=self.stop_capture,
            bg="red",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=15,
            pady=5,
            state="disabled"
        )
        self.stop_btn.pack(side="left", padx=5)
        
        self.clear_btn = tk.Button(
            button_frame,
            text="🗑 CLEAR",
            command=self.clear_all,
            bg="orange",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=15,
            pady=5
        )
        self.clear_btn.pack(side="left", padx=5)
        
        # Status bar
        self.status_label = tk.Label(
            main_frame,
            text="Status: READY | Packets: 0",
            font=("Arial", 10, "bold"),
            bg='#2b2b2b',
            fg="#00ff00"
        )
        self.status_label.pack(pady=5)
        
        # Statistics Frame
        stats_frame = tk.LabelFrame(
            main_frame, 
            text="Protocol Statistics", 
            bg='#3c3c3c', 
            fg="white", 
            font=("Arial", 10, "bold")
        )
        stats_frame.pack(fill="x", padx=10, pady=10)
        
        self.stats_labels = {}
        stats_protocols = ["TCP", "UDP", "ICMP", "ARP", "DNS", "OTHER"]
        
        stats_inner = tk.Frame(stats_frame, bg='#3c3c3c')
        stats_inner.pack(pady=5)
        
        for i, proto in enumerate(stats_protocols):
            label = tk.Label(
                stats_inner, 
                text=f"{proto}: 0", 
                width=12, 
                bg='#3c3c3c', 
                fg="#00ff00", 
                font=("Arial", 10, "bold")
            )
            label.grid(row=0, column=i, padx=15, pady=5)
            self.stats_labels[proto] = label
        
        # Packet display area
        display_label = tk.Label(
            main_frame,
            text="Captured Packets (Double-click for details)",
            font=("Arial", 11, "bold"),
            fg="white",
            bg='#2b2b2b'
        )
        display_label.pack(anchor="w", padx=10, pady=(10, 0))
        
        # Treeview for packet list
        tree_frame = tk.Frame(main_frame, bg='#2b2b2b')
        tree_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Create scrollbars
        tree_scroll_y = ttk.Scrollbar(tree_frame, orient="vertical")
        tree_scroll_x = ttk.Scrollbar(tree_frame, orient="horizontal")
        
        self.tree = ttk.Treeview(
            tree_frame,
            columns=("#", "Time", "Source", "Destination", "Protocol", "Length", "Info"),
            show="headings",
            yscrollcommand=tree_scroll_y.set,
            xscrollcommand=tree_scroll_x.set
        )
        
        tree_scroll_y.config(command=self.tree.yview)
        tree_scroll_x.config(command=self.tree.xview)
        
        # Configure columns
        self.tree.heading("#", text="#")
        self.tree.heading("Time", text="Time")
        self.tree.heading("Source", text="Source")
        self.tree.heading("Destination", text="Destination")
        self.tree.heading("Protocol", text="Protocol")
        self.tree.heading("Length", text="Length")
        self.tree.heading("Info", text="Info")
        
        self.tree.column("#", width=50)
        self.tree.column("Time", width=100)
        self.tree.column("Source", width=200)
        self.tree.column("Destination", width=200)
        self.tree.column("Protocol", width=80)
        self.tree.column("Length", width=70)
        self.tree.column("Info", width=350)
        
        # Pack treeview with scrollbars
        self.tree.grid(row=0, column=0, sticky="nsew")
        tree_scroll_y.grid(row=0, column=1, sticky="ns")
        tree_scroll_x.grid(row=1, column=0, sticky="ew")
        
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        self.tree.bind("<Double-1>", self.show_packet_details)
        
        # Payload display area
        payload_label = tk.Label(
            main_frame,
            text="Packet Details & Payload",
            font=("Arial", 11, "bold"),
            fg="white",
            bg='#2b2b2b'
        )
        payload_label.pack(anchor="w", padx=10, pady=(10, 0))
        
        self.payload_text = scrolledtext.ScrolledText(
            main_frame, 
            height=8, 
            wrap="word",
            bg='#1e1e1e', 
            fg="#00ff00",
            font=("Courier", 9)
        )
        self.payload_text.pack(fill="x", padx=10, pady=5)
    
    def populate_interfaces(self):
        """Get and populate available network interfaces"""
        try:
            interfaces = get_if_list()
            self.interface_combo['values'] = interfaces
            if interfaces:
                # Try to find a common default interface
                default_iface = None
                for iface in interfaces:
                    if iface.lower() in ['eth0', 'en0', 'wlan0', 'enp0s3']:
                        default_iface = iface
                        break
                if not default_iface and interfaces:
                    default_iface = interfaces[0]
                
                if default_iface:
                    self.interface_var.set(default_iface)
            
            self.update_status(f"Found {len(interfaces)} interface(s)", "green")
        except Exception as e:
            self.update_status(f"Error getting interfaces: {e}", "red")
            self.interface_combo['values'] = ['eth0', 'wlan0', 'en0']  # Fallback options
    
    def start_capture(self):
        """Start packet capture"""
        interface = self.interface_var.get().strip()
        
        if not interface:
            messagebox.showwarning("No Interface", "Please select a network interface")
            return
        
        # Check for admin/root permissions
        if os.name == 'nt':  # Windows
            import ctypes
            if not ctypes.windll.shell32.IsUserAnAdmin():
                response = messagebox.askyesno(
                    "Administrator Required",
                    "Packet capture requires Administrator privileges.\n\n"
                    "Do you want to restart as Administrator?"
                )
                if response:
                    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
                    self.root.quit()
                return
        else:  # Linux/Mac
            if os.geteuid() != 0:
                messagebox.showwarning(
                    "Root Required",
                    "Packet capture requires root privileges.\n\n"
                    f"Please run: sudo python3 {sys.argv[0]}"
                )
                return
        
        # Get packet limit
        try:
            packet_limit = int(self.count_var.get())
        except ValueError:
            packet_limit = 50
        
        self.is_sniffing = True
        self.packet_count = 0
        self.protocol_stats = {k: 0 for k in self.protocol_stats}
        self.stored_packets = {}
        self.update_stats()
        
        # Clear previous packets from tree
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        self.payload_text.delete(1.0, tk.END)
        
        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        
        filter_str = self.filter_var.get().strip()
        if filter_str == "":
            filter_str = None
        
        self.update_status(f"CAPTURING on {interface} - Filter: {filter_str or 'None'}", "yellow")
        
        # Start capture in separate thread
        self.sniffer_thread = threading.Thread(
            target=self.capture_packets,
            args=(interface, filter_str, packet_limit),
            daemon=True
        )
        self.sniffer_thread.start()
    
    def capture_packets(self, interface, filter_str, packet_limit):
        """Capture packets using scapy"""
        try:
            # Use a simple counter for packet limit
            captured = 0
            
            def packet_handler(pkt):
                nonlocal captured
                if not self.is_sniffing:
                    return
                captured += 1
                self.process_packet(pkt)
                if packet_limit > 0 and captured >= packet_limit:
                    self.root.after(0, self.stop_capture)
                    return True  # Stop sniffing
            
            # Start sniffing
            sniff(
                iface=interface,
                filter=filter_str,
                prn=packet_handler,
                store=False,
                stop_filter=lambda x: not self.is_sniffing
            )
            
        except PermissionError as e:
            self.root.after(0, lambda: messagebox.showerror(
                "Permission Denied",
                f"Need administrator/root privileges.\n\nError: {e}"
            ))
            self.root.after(0, self.stop_capture)
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Capture Error", str(e)))
            self.root.after(0, self.stop_capture)
    
    def process_packet(self, packet):
        """Process a captured packet"""
        self.packet_count += 1
        
        # Extract info
        info = self.extract_packet_info(packet)
        
        # Update statistics
        proto = info['protocol']
        if proto in self.protocol_stats:
            self.protocol_stats[proto] += 1
        
        # Store packet
        self.stored_packets[self.packet_count] = {
            'packet': packet,
            'info': info
        }
        
        # Update GUI
        self.root.after(0, self.update_stats)
        self.root.after(0, self.add_packet_to_display, self.packet_count, info)
    
    def extract_packet_info(self, packet):
        """Extract relevant information from packet"""
        info = {
            'timestamp': datetime.now().strftime("%H:%M:%S"),
            'src': 'N/A',
            'dst': 'N/A',
            'protocol': 'OTHER',
            'length': len(packet),
            'info': '',
            'src_port': '',
            'dst_port': ''
        }
        
        # IP Layer
        if packet.haslayer(IP):
            ip = packet[IP]
            info['src'] = ip.src
            info['dst'] = ip.dst
            
            # TCP
            if packet.haslayer(TCP):
                info['protocol'] = 'TCP'
                tcp = packet[TCP]
                info['src_port'] = tcp.sport
                info['dst_port'] = tcp.dport
                info['info'] = f"Flags: {tcp.flags}"
            
            # UDP
            elif packet.haslayer(UDP):
                info['protocol'] = 'UDP'
                udp = packet[UDP]
                info['src_port'] = udp.sport
                info['dst_port'] = udp.dport
                
                # Check for DNS
                if hasattr(packet, 'DNS'):
                    info['protocol'] = 'DNS'
                    info['info'] = "DNS Query"
            
            # ICMP
            elif packet.haslayer(ICMP):
                info['protocol'] = 'ICMP'
                icmp = packet[ICMP]
                info['info'] = f"Type: {icmp.type}"
        
        # ARP
        elif packet.haslayer(ARP):
            info['protocol'] = 'ARP'
            arp = packet[ARP]
            info['src'] = arp.psrc
            info['dst'] = arp.pdst
            info['info'] = f"ARP {arp.op}"
        
        # Format source/destination with ports
        if info['src_port']:
            info['src_display'] = f"{info['src']}:{info['src_port']}"
        else:
            info['src_display'] = info['src']
        
        if info['dst_port']:
            info['dst_display'] = f"{info['dst']}:{info['dst_port']}"
        else:
            info['dst_display'] = info['dst']
        
        return info
    
    def add_packet_to_display(self, packet_num, info):
        """Add packet to treeview"""
        self.tree.insert("", "end", values=(
            packet_num,
            info['timestamp'],
            info['src_display'],
            info['dst_display'],
            info['protocol'],
            info['length'],
            info['info'][:60]  # Truncate
        ))
        
        # Auto-scroll to bottom
        self.tree.yview_moveto(1)
        self.update_status(f"Capturing | Packets: {self.packet_count}", "yellow")
    
    def update_stats(self):
        """Update protocol statistics display"""
        for proto, count in self.protocol_stats.items():
            if proto in self.stats_labels:
                self.stats_labels[proto].config(text=f"{proto}: {count}")
    
    def show_packet_details(self, event):
        """Show detailed packet information"""
        selection = self.tree.selection()
        if not selection:
            return
        
        item = selection[0]
        values = self.tree.item(item, "values")
        if not values:
            return
        
        packet_num = int(values[0])
        
        if packet_num in self.stored_packets:
            packet_data = self.stored_packets[packet_num]
            packet = packet_data['packet']
            info = packet_data['info']
            
            # Build detailed output
            details = []
            details.append("=" * 80)
            details.append(f"PACKET #{packet_num} - {info['protocol']} Packet")
            details.append(f"Time: {info['timestamp']}")
            details.append(f"Length: {info['length']} bytes")
            details.append("-" * 80)
            
            # Ethernet
            if packet.haslayer(Ether):
                eth = packet[Ether]
                details.append(f"Ethernet: {eth.src} -> {eth.dst}")
            
            # IP
            if packet.haslayer(IP):
                ip = packet[IP]
                details.append(f"IP: {ip.src} -> {ip.dst} (TTL: {ip.ttl})")
            
            # TCP/UDP
            if packet.haslayer(TCP):
                tcp = packet[TCP]
                details.append(f"TCP: Port {tcp.sport} -> {tcp.dport}")
                details.append(f"Sequence: {tcp.seq} | ACK: {tcp.ack}")
                details.append(f"Flags: {tcp.flags}")
            elif packet.haslayer(UDP):
                udp = packet[UDP]
                details.append(f"UDP: Port {udp.sport} -> {udp.dport}")
            
            # Payload
            if packet.haslayer(Raw):
                payload = packet[Raw].load
                details.append("-" * 80)
                details.append("PAYLOAD (Hex):")
                hex_str = " ".join(f"{b:02x}" for b in payload[:200])
                if len(payload) > 200:
                    hex_str += "..."
                details.append(hex_str)
                details.append("\nPAYLOAD (ASCII):")
                ascii_str = "".join(chr(b) if 32 <= b < 127 else '.' for b in payload[:200])
                if len(payload) > 200:
                    ascii_str += "..."
                details.append(ascii_str)
            
            details.append("=" * 80)
            
            # Display in payload text area
            self.payload_text.delete(1.0, tk.END)
            self.payload_text.insert(1.0, "\n".join(details))
    
    def stop_capture(self):
        """Stop packet capture"""
        self.is_sniffing = False
        
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self.update_status(f"STOPPED - Total packets: {self.packet_count}", "green")
    
    def clear_all(self):
        """Clear all captured data"""
        if self.is_sniffing:
            self.stop_capture()
        
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        self.payload_text.delete(1.0, tk.END)
        self.packet_count = 0
        self.protocol_stats = {k: 0 for k in self.protocol_stats}
        self.stored_packets = {}
        self.update_stats()
        self.update_status("Cleared - Ready for new capture", "green")
    
    def process_packet_queue(self):
        """Process queued packets (for GUI updates)"""
        try:
            while True:
                packet_data = self.packet_queue.get_nowait()
                self.add_packet_to_display(packet_data[0], packet_data[1])
        except queue.Empty:
            pass
        finally:
            self.root.after(100, self.process_packet_queue)
    
    def update_status(self, message, color="green"):
        """Update status bar"""
        self.status_label.config(text=f"Status: {message}", fg=color)
    
    def show_help(self):
        """Show help dialog"""
        help_text = """
HOW TO USE NETWORK PACKET ANALYZER:

1. SELECT AN INTERFACE:
   - Choose your active network interface (Wi-Fi, Ethernet, etc.)
   - Click "Refresh" if your interface isn't listed

2. SET FILTERS (Optional):
   - TCP - Capture only TCP packets
   - UDP - Capture only UDP packets
   - ARP - Capture ARP packets
   - port 80 - Capture HTTP traffic
   - port 443 - Capture HTTPS traffic

3. SET PACKET LIMIT:
   - Enter number of packets to capture (0 for unlimited)

4. START CAPTURE:
   - Click the green START CAPTURE button
   - Note: Administrator/root privileges required

5. VIEW PACKETS:
   - Packets appear in the table above
   - Double-click any packet for detailed analysis

6. STOP CAPTURE:
   - Click the red STOP CAPTURE button

⚠️ IMPORTANT: Only capture on networks you own or have explicit permission!
        """
        
        help_window = tk.Toplevel(self.root)
        help_window.title("Help - How to Use")
        help_window.geometry("600x500")
        
        text_area = scrolledtext.ScrolledText(help_window, wrap="word", font=("Arial", 10))
        text_area.pack(fill="both", expand=True, padx=10, pady=10)
        text_area.insert("1.0", help_text)
        text_area.config(state="disabled")
    
    def show_about(self):
        """Show about dialog"""
        about_text = """
Network Packet Analyzer - ProDigy Infotech

Version: 1.0
Purpose: Educational packet capture and analysis tool

Features:
• Real-time packet capture
• Protocol analysis (TCP, UDP, ICMP, ARP, DNS)
• Source/destination IP and port display
• Packet payload viewing (Hex & ASCII)
• BPF filter support
• Statistics tracking

⚠️ ETHICAL USE ONLY ⚠️
This tool is for educational purposes only.
Only use on networks you own or have explicit permission to monitor.

Technologies: Python, Tkinter, Scapy
        """
        
        messagebox.showinfo("About", about_text)


def main():
    root = tk.Tk()
    app = PacketAnalyzerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
