#!/usr/bin/env bash
# Build using the official Android SDK and Java 17+ (JDK or JRE + Eclipse compiler).
# Dependencies are downloaded with TLS and checked against Google's repository checksum.
set -euo pipefail
TASK_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TASK_SDK="${ANDROID_SDK_ROOT:-${ANDROID_HOME:-/workspace/.android-sdk}}"
TASK_BUILD="$TASK_ROOT/android/app/build/manual"
TASK_OUTPUT="$TASK_ROOT/android/app/build/outputs/apk/debug"
mkdir -p "$TASK_SDK" "$TASK_BUILD" "$TASK_OUTPUT"

if ! command -v javac >/dev/null 2>&1; then
    TASK_ECJ="$TASK_SDK/ecj-3.38.0.jar"
    if [[ ! -f "$TASK_ECJ" ]]; then
        curl --fail --location --retry 2 https://repo.maven.apache.org/maven2/org/eclipse/jdt/ecj/3.38.0/ecj-3.38.0.jar --output "$TASK_ECJ"
    fi
    # Official Maven Central artifact checksum (ecj-3.38.0.jar.sha1).
    printf '%s  %s\n' 86b2e4ab1d6aef91cb21f4d2ec364afb75d05b2c "$TASK_ECJ" | sha1sum --check --status
fi

install_package() {
    local archive="$1" checksum="$2" destination="$3" extracted="$4"
    local cache="${TMPDIR:-/tmp}/aventura-android-sdk"
    mkdir -p "$cache" "$destination"
    if [[ ! -f "$cache/$archive" ]]; then
        curl --fail --location --retry 2 "https://dl.google.com/android/repository/$archive" --output "$cache/$archive"
    fi
    printf '%s  %s\n' "$checksum" "$cache/$archive" | sha1sum --check --status
    local unpack
    unpack="$(mktemp -d "$cache/unpack.XXXXXX")"
    unzip -q "$cache/$archive" -d "$unpack"
    mv "$unpack/$extracted" "$destination/"
    rmdir "$unpack"
}
if [[ ! -f "$TASK_SDK/platforms/android-35/android.jar" ]]; then
    # Checksum published in https://dl.google.com/android/repository/repository2-1.xml
    install_package platform-35_r02.zip 0bb560a90a7a2cbd0dd8348224d518b638fe7949 "$TASK_SDK/platforms" android-35
fi
if [[ ! -f "$TASK_SDK/build-tools/35.0.0/aapt2" ]]; then
    install_package build-tools_r35_linux.zip 2cfaa0bbb2336e9ec18ed3ecea84fa2e2af607bc "$TASK_SDK/build-tools" android-15
    mv "$TASK_SDK/build-tools/android-15" "$TASK_SDK/build-tools/35.0.0"
fi
TASK_TOOLS="$TASK_SDK/build-tools/35.0.0"
TASK_PLATFORM="$TASK_SDK/platforms/android-35/android.jar"
chmod u+x "$TASK_TOOLS/aapt2" "$TASK_TOOLS/d8" "$TASK_TOOLS/zipalign" "$TASK_TOOLS/apksigner"

test -s "$TASK_ROOT/public/content/words.json"
rm -rf "$TASK_BUILD/classes" "$TASK_BUILD/generated" "$TASK_BUILD/dex"
mkdir -p "$TASK_BUILD/classes" "$TASK_BUILD/generated" "$TASK_BUILD/dex"
"$TASK_TOOLS/aapt2" compile --dir "$TASK_ROOT/android/app/src/main/res" -o "$TASK_BUILD/resources.zip"
sed 's/<manifest xmlns:/<manifest package="br.com.aventuradasletras.app" xmlns:/' "$TASK_ROOT/android/app/src/main/AndroidManifest.xml" > "$TASK_BUILD/AndroidManifest.xml"
"$TASK_TOOLS/aapt2" link -I "$TASK_PLATFORM" --manifest "$TASK_BUILD/AndroidManifest.xml" --java "$TASK_BUILD/generated" -A "$TASK_ROOT/public" --version-code 1 --version-name 1.0.0 --auto-add-overlay -o "$TASK_BUILD/resources.apk" "$TASK_BUILD/resources.zip"
mapfile -d '' TASK_SOURCES < <(find "$TASK_ROOT/android/app/src/main/java" "$TASK_BUILD/generated" -name '*.java' -print0)
if command -v javac >/dev/null 2>&1; then
    javac --release 8 -encoding UTF-8 -classpath "$TASK_PLATFORM" -d "$TASK_BUILD/classes" "${TASK_SOURCES[@]}"
else
    java -jar "$TASK_ECJ" -8 -proc:none -encoding UTF-8 -classpath "$TASK_PLATFORM" -d "$TASK_BUILD/classes" "${TASK_SOURCES[@]}"
fi
mapfile -d '' TASK_CLASSES < <(find "$TASK_BUILD/classes" -name '*.class' -print0)
"$TASK_TOOLS/d8" --lib "$TASK_PLATFORM" --min-api 23 --output "$TASK_BUILD/dex" "${TASK_CLASSES[@]}"
cp "$TASK_BUILD/resources.apk" "$TASK_BUILD/unsigned.apk"
(cd "$TASK_BUILD/dex" && zip -q "$TASK_BUILD/unsigned.apk" classes*.dex)
"$TASK_TOOLS/zipalign" -f -p 4 "$TASK_BUILD/unsigned.apk" "$TASK_BUILD/aligned.apk"
TASK_KEY="${AVENTURA_DEBUG_KEYSTORE:-$TASK_SDK/aventura-debug.keystore}"
if [[ ! -f "$TASK_KEY" ]]; then
    keytool -genkeypair -keystore "$TASK_KEY" -alias androiddebugkey -keyalg RSA -keysize 2048 -validity 10000 -storepass android -keypass android -dname 'CN=Android Debug,O=Android,C=BR'
fi
"$TASK_TOOLS/apksigner" sign --ks "$TASK_KEY" --ks-key-alias androiddebugkey --ks-pass pass:android --key-pass pass:android --out "$TASK_OUTPUT/aventura-das-letras-debug.apk" "$TASK_BUILD/aligned.apk"
"$TASK_TOOLS/apksigner" verify --verbose "$TASK_OUTPUT/aventura-das-letras-debug.apk"
printf '\nAPK gerado: %s\n' "$TASK_OUTPUT/aventura-das-letras-debug.apk"
