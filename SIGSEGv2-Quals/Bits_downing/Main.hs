module Main where

import System.Environment 
import Data.List

import LambdaParser
import LambdaCalculator

main = getLine >>= getFlag . runParser lambda
