typedef struct node_structure{
  int gridNum;
  int type; //intersection type
  struct node_structure *left;
  struct node_structure *right;
} node, *pnode;

typedef struct tree_structure{
  pnode root;
} tree, *ptree;

ptree newTree();
void addNode(ptree tree, int* gNum, int* iType, int direction);
void freeTree(ptree tree);
