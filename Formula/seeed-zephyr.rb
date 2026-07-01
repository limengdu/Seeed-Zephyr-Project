# Homebrew formula for the seeed-zephyr CLI.
#
# The CLI is a pure-Python package published to PyPI as a universal wheel, so
# this formula installs that wheel directly into an isolated virtualenv.
#
# On each CLI release, update `url` and `sha256` to the new wheel listed at:
#   https://pypi.org/pypi/seeed-zephyr/<version>/json
#
# Users install via:
#   brew tap limengdu/seeed
#   brew install limengdu/seeed/seeed-zephyr

class SeeedZephyr < Formula
  desc "CLI for Seeed Studio XIAO boards with Zephyr RTOS"
  homepage "https://github.com/limengdu/Seeed-Zephyr-Project"
  url "https://files.pythonhosted.org/packages/17/93/cf7fa03f679e42032d089553bd85196fa60355d80f117d8d3a7f760d3515/seeed_zephyr-0.1.0-py3-none-any.whl", using: :nounzip
  sha256 "5f4e3dc46e8960f7a704d2ace9dfdda3f120edd6dfaac6f22c22ae78ebce1cbb"
  license "Apache-2.0"

  depends_on "python@3.12"

  def install
    # Build a standard virtualenv (with its own pip) and install the wheel into
    # it, then expose the CLI on the Homebrew prefix.
    system Formula["python@3.12"].opt_bin/"python3.12", "-m", "venv", libexec
    wheel = buildpath/"seeed_zephyr-#{version}-py3-none-any.whl"
    cp cached_download, wheel
    system libexec/"bin/python", "-m", "pip", "install", "--no-deps", wheel
    bin.install_symlink libexec/"bin/seeed-zephyr"
  end

  test do
    system bin/"seeed-zephyr", "list", "boards"
  end
end
