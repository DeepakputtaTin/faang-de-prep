def lowestCommonAncestor(root, p, q):
    # Base case
    if not root:
        return None

    # If current node is p or q → return it
    if root == p or root == q:
        return root

    # Recurse left and right
    left = lowestCommonAncestor(root.left, p, q)
    right = lowestCommonAncestor(root.right, p, q)

    # If both sides found something → current node is LCA
    if left and right:
        return root

    # Otherwise return whichever side found something
    return left or right

root = [3,5,1,6,2,0,8, null ,null,7,4]
p = 5
q = 1
lowestCommonAncestor(root, p, q)