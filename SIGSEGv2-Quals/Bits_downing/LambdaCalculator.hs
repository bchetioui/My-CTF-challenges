module LambdaCalculator where

import LambdaSyntax
import LambdaParser
import Secret

import Data.Char (isDigit)
import qualified Data.Set as Set

---------------------------
-- Convenience functions --
---------------------------

fv :: E -> Set.Set String
fv (Var x) = Set.singleton x
fv (App m n) = fv m `Set.union` fv n
fv (Abs x b) = fv b `Set.difference` Set.singleton x 

alpha :: String -> String -> E -> E
alpha n v (Var x) | x == v = Var n
alpha n v t@(Var x) = t
alpha n v (App a b) = App (alpha n v a) (alpha n v b)
alpha n v t@(Abs x b) | v == x = t
alpha n v (Abs x b) = Abs x (alpha n v b)


subst :: E -> String -> E -> E
subst n v (Var x) | v == x = n
subst n v t@(Var x) = t
subst n v (App a b) = App (subst n v a) (subst n v b)
subst n v t@(Abs x b) | v == x = t
subst n v (Abs y b) | Set.notMember y (fv n) = Abs y (subst n v b)
subst n v (Abs y b) =
  let
    y' = newVar (nextVarName y) (fv b)

    newVar yy frees | Set.member yy frees = newVar (nextVarName yy) frees
    newVar yy _ = yy
  in
    subst n v (Abs y' (alpha y' y b))

-- if s ends with a number, increment that number by one; if not, add 0 at the end
nextVarName :: String -> String
nextVarName s =
  let (prefix, num) = foldr (\a (b, c) ->
                                if (null b && isDigit a)
                                then (b, a:c)
                                else (a:b, c)) ("", "") s
  in
    prefix ++ show (if (null num) then 0 else (read num + 1))
  
hasRedex (App (Abs _ _) _) = True
hasRedex (App f a) = hasRedex f || hasRedex a
hasRedex (Abs x b) = hasRedex b
hasRedex _ = False

step :: E -> Maybe E
step (App (Abs x b) a) = return $ subst a x b -- beta
step (App f a) | hasRedex f = 
                   step f >>= \f' -> return $ App f' a
step (App f a) | hasRedex a =
                   step a >>= \a' -> return $ App f a'
step (Abs x b) | hasRedex b =
                   step b >>= \b' -> return $ Abs x b'
step _ = Nothing

eval :: E -> E
eval e = eval' e 10
  where
    eval' e 0 = error "Number of allowed steps exceeded"
    eval' e n = case step e of
                  Nothing -> e
                  Just e' -> eval' e' (n - 1)

dupAbsName :: E -> Bool
dupAbsName = dupAbsNameAux Set.empty
  where
    dupAbsNameAux ns (App f a) = (dupAbsNameAux ns f) || (dupAbsNameAux ns a)
    dupAbsNameAux ns (Var _)   = False
    dupAbsNameAux ns (Abs x b)
      | Set.member x ns = True
      | otherwise       = let newNs = ns `Set.union` (Set.singleton x) in
                            dupAbsNameAux newNs b
getFlag :: E -> IO ()
getFlag e | dupAbsName e  = error "No duplicate abstraction name allowed!"
          | dupAbsName e' = putStrLn $ "Congratulations! Flag: " ++ flag
          | otherwise     = putStrLn "No flag for you!"
  where
    e' = eval e
