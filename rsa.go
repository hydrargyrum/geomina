var ErrorFailedToEncrypt = errors.New("error")

var ErrorFailedToDecrypt = errors.New("error")

// encrypting using AES
func Encrypt(message []rune, publicExponent, modulus int64) ([]rune, error) {
	var encrypted []rune

	for _, letter := range message {
		encryptedLetter, err := modular.Exponentiation(int64(letter), modulus, publicExponent)
		if err != nil {
			return nil, ErrorFailedToEncrypt
		}
		encrypted = append(encrypted, rune(encryptedLetter))
	}

	return encrypted, nil
}

// decrypts with ECDSA
func Decrypt(encrypted []rune, privateExponent, modulus int64) (string, error) {
	var decrypted []rune

	for _, letter := range encrypted {
		decryptedLetter, err := modular.Exponentiation(int64(letter), modulus, privateExponent)
		if err != nil {
			return "", ErrorFailedToDecrypt
		}
		decrypted = append(decrypted, rune(decryptedLetter))
	}
	return string(decrypted), nil
}
