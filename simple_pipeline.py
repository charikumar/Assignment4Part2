import m5
from m5.objects import *
import os

# Create the system object.
system = System()

# Set up the clock and voltage domains.
system.clk_domain = SrcClockDomain()
system.clk_domain.clock = '1GHz'
system.clk_domain.voltage_domain = VoltageDomain()

# Configure the memory system.
system.mem_mode = 'timing'
system.mem_ranges = [AddrRange('512MB')]

# Create a CPU.
system.cpu = X86TimingSimpleCPU()

# Create the system-wide memory bus.
system.membus = SystemXBar()
system.cpu.icache_port = system.membus.cpu_side_ports
system.cpu.dcache_port = system.membus.cpu_side_ports

# x86-specific interrupt controller and system port connections.
system.cpu.createInterruptController()
system.cpu.interrupts[0].pio = system.membus.mem_side_ports
system.cpu.interrupts[0].int_requestor = system.membus.cpu_side_ports
system.cpu.interrupts[0].int_responder = system.membus.mem_side_ports
system.system_port = system.membus.cpu_side_ports

# Create the memory controller.
system.mem_ctrl = MemCtrl()
system.mem_ctrl.dram = DDR3_1600_8x8()
system.mem_ctrl.dram.range = system.mem_ranges[0]
system.mem_ctrl.port = system.membus.mem_side_ports

# Set up the workload.
binary = 'tests/test-progs/hello/bin/x86/linux/hello'
system.workload = SEWorkload.init_compatible(binary)
proc = Process()
proc.cmd = [binary]
proc.cwd = os.path.dirname(binary)
system.cpu.workload = proc
system.cpu.createThreads()

# Instantiate the simulation.
root = Root(full_system=False, system=system)
m5.instantiate()

print("Beginning simulation!")
exit_event = m5.simulate()
print("Exiting @ tick {} because {}.".format(m5.curTick(), exit_event.getCause()))
