# Homebrew formula for seeed-zephyr CLI.
#
# This formula is a template. To use it:
#   1. Publish the package to PyPI
#   2. Update `url` to the PyPI sdist URL
#   3. Update `sha256` with: shasum -a 256 seeed_zephyr-<version>.tar.gz
#   4. Host this file in a Homebrew tap repository
#
# Users install via:
#   brew tap seeed-studio/seeed
#   brew install seeed-studio/seeed/seeed-zephyr

class SeeedZephyr < Formula
  include Language::Python::Virtualenv

  desc "CLI for Seeed Studio XIAO boards with Zephyr RTOS"
  homepage "https://github.com/Seeed-Projects/seeed-zephyr-base"
  url "https://files.pythonhosted.org/packages/source/s/seeed-zephyr/seeed_zephyr-0.1.0.tar.gz"
  sha256 "PLACEHOLDER_UPDATE_AFTER_PYPI_PUBLISH"
  license "Apache-2.0"

  depends_on "python@3.12"

  def install
    virtualenv_install_with_resources
  end

  test do
    system bin / "seeed-zephyr", "list", "boards"
  end
end
