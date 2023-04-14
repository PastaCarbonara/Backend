with open("requirements.txt", "r", encoding="utf-16") as f:
    old_req = f.read()
    old_req = old_req.split("\n")

with open("new_req.txt", "r", encoding="utf-16") as f:
    new_req = f.read()
    new_req = new_req.split("\n")

result = {"missing": [], "different": []}

for old in old_req:
    for new in new_req:
        x_new = new.split("==")
        x_old = old.split("==")

        if x_new[0] == x_old[0]:
            if x_new[1] != x_old[1]:
                result["different"].append((x_new[0], x_new[1], x_old[1]))
            break
    else:
        result["missing"].append(old)

print("Missing:")
for i in result["missing"]:
    print(i.split("==")[0])

# print("\nDifferent:")
# for i in result["different"]:
#     print(i[0], "\t", i[1], "->\t", i[2])

# print(old_req)
# print(new_req)