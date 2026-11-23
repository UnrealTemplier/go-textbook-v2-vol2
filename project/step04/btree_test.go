package step04

import "testing"

func TestBPlusTreeAndCostPlanner(t *testing.T) {
	tree := NewBPlusTree(4)
	for i := int64(1); i <= 100; i++ {
		tree.Insert(i*10, "ctid")
	}
	if tree.Height() < 3 || tree.Splits() == 0 {
		t.Fatalf("expected splits and height >= 3, got height=%d splits=%d", tree.Height(), tree.Splits())
	}
	if v, ok := tree.Search(420); !ok || v != "ctid" {
		t.Fatalf("expected key 420 to be found")
	}
	if _, ok := tree.Search(425); ok {
		t.Fatalf("expected key 425 to be absent")
	}

	r := tree.RangeScan(250, 310)
	want := []int64{250, 260, 270, 280, 290, 300, 310}
	if len(r) != len(want) {
		t.Fatalf("range len=%d want=%d (%v)", len(r), len(want), r)
	}
	for i := range want {
		if r[i] != want[i] {
			t.Fatalf("range[%d]=%d want=%d", i, r[i], want[i])
		}
	}

	if plan, _ := EstimatePlan(10000, 1_000_000, 0.0001, true); plan != PlanIndexOnlyScan {
		t.Fatalf("expected Index-Only Scan for selective covered query, got %s", plan)
	}
	if plan, _ := EstimatePlan(10000, 1_000_000, 0.0001, false); plan != PlanIndexScan {
		t.Fatalf("expected Index Scan for selective query, got %s", plan)
	}
	if plan, _ := EstimatePlan(10000, 1_000_000, 0.45, false); plan != PlanSeqScan {
		t.Fatalf("expected Seq Scan for low selectivity 45%%, got %s", plan)
	}
}
