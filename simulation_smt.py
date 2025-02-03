import m5
from m5.objects import *
import os

# --------------------------
# Basic System Configuration
# --------------------------
system = System()

# Set up the clock and voltage domains.
system.clk_domain = SrcClockDomain()
system.clk_domain.clock = '1GHz'
system.clk_domain.voltage_domain = VoltageDomain()

# Configure the memory system.
system.mem_mode = 'timing'
system.mem_ranges = [AddrRange('512MB')]

# --------------------------
# SMT CPU Configuration
# --------------------------
# Use an out-of-order CPU (DerivO3CPU) and enable SMT (2 threads per core).
system.cpu = DerivO3CPU()
system.cpu.numThreads = 2  # Enable 2 hardware threads.
# Configure superscalar widths (example values for a 4-issue machine).
system.cpu.fetchWidth  = 4
system.cpu.decodeWidth = 4
system.cpu.renameWidth = 4
system.cpu.issueWidth  = 4
system.cpu.commitWidth = 4
# Set a branch predictor (here, TournamentBP).
system.cpu.branchPred  = TournamentBP()

# --------------------------
# Interconnect Configuration
# --------------------------
system.membus = SystemXBar()
system.cpu.icache_port = system.membus.cpu_side_ports
system.cpu.dcache_port = system.membus.cpu_side_ports

# x86-specific interrupt controller and system port connections.
system.cpu.createInterruptController()
system.cpu.interrupts[0].pio           = system.membus.mem_side_ports
system.cpu.interrupts[0].int_requestor = system.membus.cpu_side_ports
system.cpu.interrupts[0].int_responder = system.membus.mem_side_ports
system.system_port = system.membus.cpu_side_ports

# --------------------------
# Memory Controller
# --------------------------
system.mem_ctrl = MemCtrl()
system.mem_ctrl.dram = DDR3_1600_8x8()
system.mem_ctrl.dram.range = system.mem_ranges[0]
system.mem_ctrl.port = system.membus.mem_side_ports

# --------------------------
# Workload Configuration
# --------------------------
binary = 'tests/test-progs/hello/bin/x86/linux/hello'
system.workload = SEWorkload.init_compatible(binary)

# Create two separate Process objects (with unique PIDs) for the two SMT threads.
proc1 = Process()
proc1.cmd = [binary]
proc1.cwd = os.path.dirname(binary)
proc1.pid = 100  # Unique PID for thread 0.

proc2 = Process()
proc2.cmd = [binary]
proc2.cwd = os.path.dirname(binary)
proc2.pid = 101  # Unique PID for thread 1.

# Assign these processes to the CPU's SMT threads.
system.cpu.workload = [proc1, proc2]

# IMPORTANT: Call createThreads() after setting numThreads and workload.
system.cpu.createThreads()

# --------------------------
# Instantiate and Run Simulation
# --------------------------
root = Root(full_system=False, system=system)
m5.instantiate()

print("Beginning SMT simulation!")
exit_event = m5.simulate()
print("Exiting @ tick {} because {}.".format(m5.curTick(), exit_event.getCause()))
