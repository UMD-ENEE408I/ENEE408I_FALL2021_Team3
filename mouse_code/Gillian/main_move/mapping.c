#include "mapping.h"
#include <stdio.h>
#include <stdlib.h>

ptree newTree(){
  ptree new = (ptree) malloc(sizeof(tree));
  new->root = NULL;
  return new;
}

void addNode(ptree treeMap, int gNum, int iType, int direction){
  pnode cur;
  pnode n = (pnode) malloc(sizeof(node)); //malloc node to be added
  n->gridNum = gNum;
  n->type = iType;
  n->left = NULL;
  n->right = NULL;

  if (!treeMap->root)  //insert at root
    treeMap->root = n;
  else
    cur = treeMap->root;

  //TODO: want to store new node directly off of current node...
}
