module LambdaSyntax where

import Data.List (intercalate)

data E = Var String
       | App E E
       | Abs String E
         deriving (Eq, Show)
