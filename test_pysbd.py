
import pysbd

def test_pysbd():
    splitter = pysbd.Segmenter(language="en", clean=False)
    
    # Text with abbreviations that breaks the old regex
    text1 = "Jones was already snoring. Mrs. Jones was asleep."
    text2 = "Mr. Pilkington was an easy-going gentleman farmer."
    text3 = "Dr. Strange is a doctor."
    text4 = "U.S.A. is a country."
    
    print(f"Test 1: {splitter.segment(text1)}")
    print(f"Test 2: {splitter.segment(text2)}")
    print(f"Test 3: {splitter.segment(text3)}")
    print(f"Test 4: {splitter.segment(text4)}")

if __name__ == "__main__":
    test_pysbd()
