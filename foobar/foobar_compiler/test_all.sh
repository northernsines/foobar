#!/bin/bash
# FOOBAR Compiler Test Suite
# Verifies all examples compile and run correctly

echo "╔════════════════════════════════════════╗"
echo "║  FOOBAR Compiler Test Suite            ║"
echo "╚════════════════════════════════════════╝"
echo ""

cd compiler

PASSED=0
FAILED=0

# Function to test a file
test_file() {
    local file=$1
    local name=$(basename "$file" .foob)
    
    echo "Testing: $name"
    
    # Compile
    python3 foobar.py compile "../examples/$file" -o "../examples/$name" 2>&1 > /tmp/foobar_test.log
    
    if grep -q "Successfully compiled" /tmp/foobar_test.log; then
        # Run
        "../examples/$name" > /dev/null 2>&1
        
        if [ $? -eq 0 ]; then
            echo "  ✓ PASSED"
            ((PASSED++))
        else
            echo "  ✗ FAILED (runtime error)"
            ((FAILED++))
        fi
    else
        echo "  ✗ FAILED (compilation error)"
        ((FAILED++))
    fi
}

# Test all examples
test_file "class_test.foob"
test_file "functional_test.foob"
test_file "inheritance_test.foob"
test_file "multi_inheritance_test.foob"
test_file "isa_test.foob"
test_file "comparison_test.foob"
test_file "comprehensive_test.foob"
test_file "showcase.foob"

echo ""
echo "════════════════════════════════════════"
echo "Results: $PASSED passed, $FAILED failed"
echo "════════════════════════════════════════"

if [ $FAILED -eq 0 ]; then
    echo "🎉 All tests passed!"
    exit 0
else
    echo "❌ Some tests failed"
    exit 1
fi
