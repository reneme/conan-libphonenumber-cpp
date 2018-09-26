#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, CMake, tools
import os


class LibphonenumberCppConan(ConanFile):
    name = "libphonenumber-cpp"
    version = "8.9.14"
    description = "Google's common C++ library for parsing, formatting, and validating international phone numbers."
    url = "https://github.com/hrantzsch/conan-libphonenumber-cpp"
    homepage = "https://github.com/googlei18n/libphonenumber"
    author = "Hannes Rantzsch <gh@hannesrantzsch.de>, René Meusel <github@renemeusel.de>"
    license = "Apache-2.0"
    exports = ["LICENSE"]

    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"

    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = "shared=False", "fPIC=True"

    source_subfolder = "source_subfolder"
    build_subfolder = "build_subfolder"

    requires = (
        "gtest/[>=1.8.1]@bincrafters/stable",
        "protobuf/[>=3.6]@bincrafters/stable",
        "icu/[>=60]@bincrafters/stable"
    )

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def source(self):
        tools.get("{0}/archive/v{1}.tar.gz".format(self.homepage, self.version))
        extracted_dir = "libphonenumber-" + self.version

        os.rename(extracted_dir, self.source_subfolder)

    def configure_cmake(self):
        cmake = CMake(self)

        cmake.definitions["USE_BOOST"] = False

        # TODO: only for GCC
        cmake.definitions["CMAKE_CXX_FLAGS"]   = "-Wno-error=sign-compare"
        cmake.definitions["CMAKE_PREFIX_PATH"] = ";".join([ self.deps_cpp_info["gtest"].rootpath , self.deps_cpp_info["protobuf"].rootpath , self.deps_cpp_info["icu"].rootpath ])

        if self.settings.os != 'Windows':
            cmake.definitions['CMAKE_POSITION_INDEPENDENT_CODE'] = self.options.fPIC
        cmake.configure(source_folder=os.path.join(self.source_subfolder, "cpp"), build_folder=self.build_subfolder)
        return cmake

    def build(self):
        cmake = self.configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self.source_subfolder)
        cmake = self.configure_cmake()
        cmake.install()
        # If the CMakeLists.txt has a proper install method, the steps below may be redundant
        # If so, you can just remove the lines below
        include_folder = os.path.join(self.source_subfolder, "include")
        self.copy(pattern="*", dst="include", src=include_folder)
        self.copy(pattern="*.dll", dst="bin", keep_path=False)
        self.copy(pattern="*.lib", dst="lib", keep_path=False)
        self.copy(pattern="*.a", dst="lib", keep_path=False)
        self.copy(pattern="*.so*", dst="lib", keep_path=False)
        self.copy(pattern="*.dylib", dst="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
