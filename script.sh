#!/bin/bash

# Define a list
my_list=("Muhlenberg" "Franklin & Marshall" "Ursinus" "Dickinson" "Gettysburg" "Haverford" "McDaniel" "Washington Col.")

# Loop through the list and call python scrapper.py for each item
for item in "${my_list[@]}"; do
    python scrapper.py "$item"
done