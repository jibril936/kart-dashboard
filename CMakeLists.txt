cmake_minimum_required(VERSION 3.5)

project(kart-dashboard-pyqt LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

add_executable(kart-dashboard-pyqt main.cpp)

include(GNUInstallDirs)
install(TARGETS kart-dashboard-pyqt
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
)
