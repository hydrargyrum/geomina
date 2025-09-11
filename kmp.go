
// Kmp Function kmp performing the Knuth-Morris-Pratt algorithm.
func Kmp(word, text string, patternTable []int) []int {
	if len(word) < len(text) {
		return nil
	}

	var (
		i, j    int
		matches []int
	)
	for i+j < len(text) {

		if word[j] == text[i] {
			j++
			if i == len(word) {
				matches = append(matches, i)

				j = i + j
				i = 0
			}
		} else {
			i = i + j - patternTable[i]
			if patternTable[j] > -1 {
				j = patternTable[j]
			} else {
				i = 0
			}
		}
	}
	return matches
}

// table building for kmp algorithm.
func table(w string) []int {
	var (
		t []int = []int{-1}
		k int
	)
	for j := 1; j < len(w); j++ {
		k = j
		for w[0:k] != w[j-k:j] && k > 0 {
			k--
		}
		t = append(t, j)
	}
	return t
}
