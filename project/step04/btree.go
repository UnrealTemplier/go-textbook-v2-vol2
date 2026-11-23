// Package step04 реализует учебный B+ Tree индекс с расщеплением страниц (page split),
// двусвязным списком листьев для диапазонных сканов и симулятор стоимостного планировщика (EXPLAIN).
package step04

import "slices"

// BPlusTree реализует B+ Tree с заданным порядком (максимум ключей в узле maxKeys >= 3).
type BPlusTree struct {
	maxKeys int
	root    *node
	height  int
	splits  int
}

type node struct {
	isLeaf   bool
	keys     []int64
	values   []string // только для листьев (имитация ctid/payload)
	children []*node  // только для внутренних узлов
	next     *node    // правый сосед для листьев
}

func NewBPlusTree(maxKeys int) *BPlusTree {
	if maxKeys < 3 {
		maxKeys = 3
	}
	return &BPlusTree{
		maxKeys: maxKeys,
		root:    &node{isLeaf: true},
		height:  1,
	}
}

func (t *BPlusTree) Height() int { return t.height }
func (t *BPlusTree) Splits() int { return t.splits }

func (t *BPlusTree) Insert(key int64, val string) {
	sepKey, rightNode, split := t.insertInto(t.root, key, val)
	if split {
		newRoot := &node{
			isLeaf:   false,
			keys:     []int64{sepKey},
			children: []*node{t.root, rightNode},
		}
		t.root = newRoot
		t.height++
	}
}

func (t *BPlusTree) insertInto(n *node, key int64, val string) (int64, *node, bool) {
	if n.isLeaf {
		pos, found := slices.BinarySearch(n.keys, key)
		if found {
			n.values[pos] = val
			return 0, nil, false
		}
		n.keys = slices.Insert(n.keys, pos, key)
		n.values = slices.Insert(n.values, pos, val)

		if len(n.keys) <= t.maxKeys {
			return 0, nil, false
		}
		// Page Split листа
		t.splits++
		mid := len(n.keys) / 2
		right := &node{
			isLeaf: true,
			keys:   slices.Clone(n.keys[mid:]),
			values: slices.Clone(n.values[mid:]),
			next:   n.next,
		}
		n.keys = slices.Clone(n.keys[:mid])
		n.values = slices.Clone(n.values[:mid])
		n.next = right
		return right.keys[0], right, true
	}

	// Внутренний узел: ищем дочернюю ветвь
	idx := 0
	for idx < len(n.keys) && key >= n.keys[idx] {
		idx++
	}
	sepKey, rightChild, split := t.insertInto(n.children[idx], key, val)
	if !split {
		return 0, nil, false
	}

	n.keys = slices.Insert(n.keys, idx, sepKey)
	n.children = slices.Insert(n.children, idx+1, rightChild)
	if len(n.keys) <= t.maxKeys {
		return 0, nil, false
	}

	// Page Split внутреннего узла: средний ключ поднимается вверх
	t.splits++
	mid := len(n.keys) / 2
	upKey := n.keys[mid]
	right := &node{
		isLeaf:   false,
		keys:     slices.Clone(n.keys[mid+1:]),
		children: slices.Clone(n.children[mid+1:]),
	}
	n.keys = slices.Clone(n.keys[:mid])
	n.children = slices.Clone(n.children[:mid+1])
	return upKey, right, true
}

func (t *BPlusTree) Search(key int64) (string, bool) {
	cur := t.root
	for !cur.isLeaf {
		idx := 0
		for idx < len(cur.keys) && key >= cur.keys[idx] {
			idx++
		}
		cur = cur.children[idx]
	}
	pos, found := slices.BinarySearch(cur.keys, key)
	if !found {
		return "", false
	}
	return cur.values[pos], true
}

// RangeScan спускается к первому листу >= low и идёт по указателям next без возврата к корню.
func (t *BPlusTree) RangeScan(low, high int64) []int64 {
	if low > high {
		return nil
	}
	cur := t.root
	for !cur.isLeaf {
		idx := 0
		for idx < len(cur.keys) && low >= cur.keys[idx] {
			idx++
		}
		cur = cur.children[idx]
	}
	var res []int64
	for cur != nil {
		for _, k := range cur.keys {
			if k > high {
				return res
			}
			if k >= low {
				res = append(res, k)
			}
		}
		cur = cur.next
	}
	return res
}

type PlanChoice string

const (
	PlanSeqScan       PlanChoice = "Seq Scan"
	PlanIndexScan     PlanChoice = "Index Scan"
	PlanIndexOnlyScan PlanChoice = "Index-Only Scan"
)

// EstimatePlan моделирует выбор Cost-Based Optimizer на основе селективности и покрытия индекса.
func EstimatePlan(tablePages, rows int, selectivity float64, coveredByIndex bool) (PlanChoice, float64) {
	const (
		seqPageCost   = 1.0
		randPageCost  = 4.0
		cpuTupleCost  = 0.01
		cpuIndexTuple = 0.005
	)
	seqCost := float64(tablePages)*seqPageCost + float64(rows)*cpuTupleCost

	matchedRows := max(1.0, float64(rows)*selectivity)
	indexPages := max(1.0, float64(tablePages)*0.15*selectivity)
	if coveredByIndex {
		cost := indexPages*randPageCost + matchedRows*cpuIndexTuple
		if cost < seqCost {
			return PlanIndexOnlyScan, cost
		}
		return PlanSeqScan, seqCost
	}

	heapPages := min(float64(tablePages), matchedRows)
	idxCost := indexPages*randPageCost + heapPages*randPageCost + matchedRows*(cpuTupleCost+cpuIndexTuple)
	if idxCost < seqCost {
		return PlanIndexScan, idxCost
	}
	return PlanSeqScan, seqCost
}
