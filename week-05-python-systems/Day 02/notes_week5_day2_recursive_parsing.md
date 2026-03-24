# Week 5 Day 2 — Recursive Parsing
**FAANG DE Prep | 13-Week Plan**

---

## 🧠 Core Theory

### What is Recursion?
- A function that calls **itself** until a base case is reached
- Break big problem into smaller identical subproblems
- Always needs: **Base case** (stop condition) + **Recursive case** (smaller subproblem)

### Recursion Template
```python
def recursive_fn(problem):
    # Base case — when to stop
    if base_condition:
        return base_value
    
    # Recursive case — smaller subproblem
    return recursive_fn(smaller_problem)
```

### Binary Tree Basics
- Hierarchical structure, max 2 children (left, right)
- Used for efficient storage and retrieval
- **TreeNode class:**
```python
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right
```

---

## 💻 Problems Solved

### LC 236 — Lowest Common Ancestor of Binary Tree

**Definition:** LCA = deepest node that has both p and q as descendants.

```
        3
       / \
      5   1
     / \ / \
    6  2 0  8
      / \
     7   4

LCA(5, 1) → 3  (different subtrees)
LCA(5, 4) → 5  (5 is ancestor of 4)
LCA(6, 4) → 5  (both under 5)
```

**3 Cases:**
1. Current node is p or q → return it
2. p and q in different subtrees → current node is LCA
3. p and q in same subtree → recurse into that side

```python
class Solution(object):
    def lowestCommonAncestor(self, root, p, q):
        # Base case — reached end of tree
        if not root:
            return None
        
        # Current node is p or q
        if root == p or root == q:
            return root
        
        # Recurse both sides
        left = self.lowestCommonAncestor(root.left, p, q)   # ← self. required!
        right = self.lowestCommonAncestor(root.right, p, q)
        
        # Both sides found something → current node is LCA
        if left and right:
            return root
        
        # One side found something → propagate up
        return left or right

# Time: O(N) — visits every node once
# Space: O(H) — H = tree height (recursion stack)
```

---

## ⚠️ Critical LeetCode Gotcha

```python
# Wrong ❌ — NameError: global name not defined
left = lowestCommonAncestor(root.left, p, q)

# Correct ✅ — always use self inside class Solution
left = self.lowestCommonAncestor(root.left, p, q)
```

**Rule:** Inside `class Solution` on LeetCode, all recursive calls need `self.methodName()`.

---

## 🔗 DE Connections

| Recursive Pattern | Real DE Use Case |
|---|---|
| LCA on tree | Data lineage — finding common ancestor of two assets |
| Tree traversal | Airflow DAG — finding merge point of two pipeline branches |
| Recursive JSON flatten | Kafka event normalization before Snowflake load |
| Tree depth | Measuring pipeline complexity in data catalogs |

---

## 📝 Warm-Up Recall (for tomorrow)

1. What are the two required parts of any recursive function?
2. In LCA, what does it mean when both `left` and `right` are non-null?
3. Why do recursive calls inside `class Solution` need `self.`?
4. What is the space complexity of tree recursion and why?

---
*Week 5 Day 2 Complete ✅*
*Commit: `week-05: day 2 complete - recursive parsing, LC236 LCA binary tree`*
