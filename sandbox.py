# sandbox.py

previous_scan = [
    {"port": 22, "service": "SSH"},
    {"port": 80, "service": "HTTP"},
    {"port": 443, "service": "HTTPS"},
    {"port": 3306, "service": "MySQL"}
]

current_scan = [
    {"port": 80, "service": "HTTP"},
    {"port": 443, "service": "HTTPS"},
    {"port": 8080, "service": "HTTP-Proxy"}
]

# 1. Extract just the port numbers into sets so you can do your math
# Hint: You can use a list comprehension like [item["port"] for item in previous_scan]
prev_port_nums = set([item["port"] for item in previous_scan]) # Update this
crnt_port_nums = set([port["port"] for port in current_scan]) # Update this

# 2. Do your set math to find the changes
newly_opened_nums = set(crnt_port_nums - prev_port_nums) # Update this
newly_closed_nums = set(prev_port_nums - crnt_port_nums) # Update this

print("newly_opened_nums : " , newly_opened_nums)
print("newly_closed_nums : " , newly_closed_nums)

# 3. Now, write loops to find the FULL dictionary for the changed ports
newly_opened_details = []
# Write a loop that checks current_scan for the ports in newly_opened_nums
for item in current_scan:
    if item["port"] in newly_opened_nums:
        newly_opened_details.append(item)


newly_closed_details = []
# Write a loop that checks previous_scan for the ports in newly_closed_nums
for item in previous_scan:
    if item["port"] in newly_closed_nums:
        newly_closed_details.append(item)


print(f"Newly opened details: {newly_opened_details}")
print(f"Newly closed details: {newly_closed_details}")