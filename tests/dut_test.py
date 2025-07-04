import cocotb
from cocotb.triggers import RisingEdge, Timer
from cocotb.clock import Clock


 # Write to DUT Register
async def write_reg(dut, address, data):
    dut.write_en.value = 1
    dut.write_address.value = address
    dut.write_data.value = data
    await RisingEdge(dut.CLK)
    dut.write_en.value = 0
    await RisingEdge(dut.CLK)  # wait for write_rdy to settle


# Read from DUT Register
async def read_reg(dut, address):
    dut.read_en.value = 1
    dut.read_address.value = address
    await RisingEdge(dut.CLK)
    dut.read_en.value = 0
    await RisingEdge(dut.CLK)
    return int(dut.read_data.value)


@cocotb.test()
async def or_gate_test(dut):
    """Test OR Gate via Register Interface"""

    # Start clock
    cocotb.start_soon(Clock(dut.CLK, 10, units="ns").start())

    # Reset DUT
    dut.RST_N.value = 0
    await Timer(20, units="ns")
    dut.RST_N.value = 1
    await Timer(20, units="ns")

    # Test all combinations of A and B
    for a in [0, 1]:
        for b in [0, 1]:
            # Write A and B to respective registers
            await write_reg(dut, 4, a)  # A_Data at address 4
            await write_reg(dut, 5, b)  # B_Data at address 5

            # Wait for DUT to compute
            await Timer(10, units="ns")

            # Read output from address 3 (y_output)
            y = await read_reg(dut, 3)

            # Check expected output
            expected = a | b
            assert y == expected, f"Test failed: A={a}, B={b}, Got Y={y}, Expected={expected}"
