import Prelude hiding(lookup)
 
data BinaryTree k v = Nil | Node k v (BinaryTree k v) (BinaryTree k v) deriving(Show)

lookup :: Ord k => k -> BinaryTree k v -> Maybe v
lookup val Nil = Nothing
lookup val (Node x v l r) | val == x   = Just v
                          | val < x    = lookup val l 
                          | otherwise  = lookup val r

insert :: Ord k => k -> v -> BinaryTree k v -> BinaryTree k v
insert key val Nil = Node key val Nil Nil
insert key val (Node x v l r) | key == x  = Node key val l r
                              | key < x   = Node x v (insert key val l) r
                              | otherwise = Node x v l (insert key val r)

merge' :: Ord k => BinaryTree k v -> BinaryTree k v -> BinaryTree k v
merge' Nil tree = tree
merge' tree Nil = tree
merge' (Node x v l r) t2 = Node x v l (merge' r t2)

delete :: Ord k => k -> BinaryTree k v -> BinaryTree k v
delete key Nil = Nil
delete key (Node x v l r) | key == x  = merge' l r
                          | key < x   = Node x v (delete key l) r
                          | otherwise = Node x v l (delete key r)
