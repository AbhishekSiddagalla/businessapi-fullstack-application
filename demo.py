matrix = [[1,2,3],[4,5,6],[7,8,9]]

A = matrix
n = len(A)
m = n//2
print(f"length of matrix: {n}")
print(f"length of half matrix: {m}")

for i in range(n):
    for j in range(i):
        A[i][j], A[j][i] = A[j][i], A[i][j]
print(A) # Transposed
# [[1, 4, 7],
#  [2, 5, 8],
#  [3, 6, 9]]

for i in range(n):
    for j in range(m):
        print(n, j)
        A[i][j], A[i][n-j-1] = A[i][n-j-1], A[i][j]

print(A)
