package step00

import "testing"

func TestGreeting(t *testing.T) {
	got := Greeting("Go")
	want := "Привет, Go!"
	if got != want {
		t.Fatalf("got %q, want %q", got, want)
	}
}
