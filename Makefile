CC ?= clang
LD ?= ld
CONFORMANCE ?= ../typing/conformance
UPSTREAM ?= ../ultrafaster/ultrafaster
MACOS_SDK := $(shell xcrun --sdk macosx --show-sdk-path)
PAYLOAD_SIZE := $(shell stat -f%z src/payload.bin)

.PHONY: all benchmark clean oracle verify

all: ultrafastest

ultrafastest: src/ultrafastest.S src/payload.bin
	$(CC) -target arm64-apple-macos11 -DPAYLOAD_SIZE=$(PAYLOAD_SIZE) \
		-c -o src/ultrafastest.o src/ultrafastest.S
	$(LD) -arch arm64 -e _start -platform_version macos 11.0 15.0 \
		-no_data_in_code_info -no_function_starts -no_source_version \
		-no_uuid -x \
		-syslibroot $(MACOS_SDK) -lSystem -o $@ src/ultrafastest.o

oracle:
	uv run scripts/generate_payload.py $(CONFORMANCE) src/payload.bin

verify: ultrafastest
	uv run scripts/verify.py $(CONFORMANCE) ./ultrafastest

benchmark: ultrafastest
	uv run scripts/benchmark.py $(CONFORMANCE) ./ultrafastest $(UPSTREAM)

clean:
	rm -f ultrafastest src/ultrafastest.o
