/*
====================================================================
 Jenkinsfile
 Selenium + Pytest Automation Framework
====================================================================

Purpose:
    This Jenkins pipeline will:

    1. Checkout the latest source code
    2. Verify Python installation
    3. Install project dependencies
    4. Run Smoke tests
    5. Run Regression tests
    6. Generate pytest HTML reports
    7. Publish HTML reports in Jenkins
    8. Archive screenshots
    9. Display build status

Technology:
    - Python
    - Selenium
    - Pytest
    - pytest-html
    - Jenkins
====================================================================
*/


pipeline {

    /*
    ================================================================
    AGENT
    ================================================================

    `agent any` means Jenkins can run this pipeline on any
    available Jenkins agent/node.

    The Jenkins machine must have:
        - Python
        - Chrome
        - Selenium-compatible environment
    ================================================================
    */
    agent any
    /*

    ================================================================
    ENVIRONMENT VARIABLES
    ================================================================

    PYTHONUNBUFFERED=1 makes Python output appear immediately
    in the Jenkins console instead of being buffered.

    This is useful for seeing messages such as:

        ✅ TC-SB01-P PASSED
        ✅ TC-SB02-P PASSED

    directly in Jenkins Console Output.
    ================================================================
    */
    environment {

        PYTHONUNBUFFERED = '1'

    }
    /*

    ================================================================
    STAGES
    ================================================================
    */

    stages {

        /*
        ============================================================
        STAGE 1 - CHECKOUT
        ============================================================

        Gets the latest source code from Git.

        If Jenkins is connected to GitHub/GitLab/Bitbucket,
        `checkout scm` checks out the branch configured in
        the Jenkins job.
        ============================================================
        */

        stage('Checkout') {

            steps {

                echo '=========================================='
                echo '        CHECKOUT SOURCE CODE'
                echo '=========================================='

                checkout scm

            }
        }


        /*
        ============================================================
        STAGE 2 - PYTHON ENVIRONMENT
        ============================================================

        Verify that Python and pip are available on the Jenkins
        machine.

        Equivalent commands when running locally:

            python --version
            python -m pip --version
        ============================================================
        */

        stage('Python Environment') {

            steps {

                echo '=========================================='
                echo '        PYTHON ENVIRONMENT'
                echo '=========================================='

                /*
                Check installed Python version.
                */

                bat 'python --version'


                /*
                Check pip installation.
                */

                bat 'python -m pip --version'

            }
        }


        /*
        ============================================================
        STAGE 3 - INSTALL DEPENDENCIES
        ============================================================

        Installs all Python packages listed inside:

            requirements.txt

        Example requirements.txt:

            pytest
            selenium
            pytest-html
            allure-pytest

        Using:

            python -m pip

        is safer than calling `pip` directly because it ensures
        pip belongs to the Python interpreter being used.
        ============================================================
        */

        stage('Install Dependencies') {

            steps {

                echo '=========================================='
                echo '        INSTALLING DEPENDENCIES'
                echo '=========================================='


                /*
                Upgrade pip.

                This is optional but helps avoid old pip issues.
                */

                bat '''
                    python -m pip install --upgrade pip
                '''


                /*
                Install all project dependencies.

                Jenkins reads requirements.txt from the project root.
                */

                bat '''
                    python -m pip install -r requirements.txt
                '''

            }
        }


        /*
        ============================================================
        STAGE 4 - CREATE REPORT DIRECTORY
        ============================================================

        Creates the reports directory if it doesn't already exist.

        pytest-html will place the generated HTML reports here.

        Example:

            reports/
                smoke-report.html
                regression-report.html
        ============================================================
        */

        stage('Create Reports Directory') {

            steps {

                echo '=========================================='
                echo '        CREATING REPORT DIRECTORY'
                echo '=========================================='

                bat '''
                    if not exist reports mkdir reports
                '''

            }
        }


        /*
        ============================================================
        STAGE 5 - RUN SMOKE TESTS
        ============================================================

        Runs only tests marked with:

            @pytest.mark.smoke

        Example:

            @pytest.mark.smoke
            def test_tc01_p_login_page_loads():
                ...

        Command:

            python -m pytest
                -m smoke
                -v
                --html=reports/smoke-report.html
                --self-contained-html

        -m smoke
            Run only smoke tests.

        -v
            Verbose output.

        --html
            Generate HTML test report.

        --self-contained-html
            Put CSS/JS inside the HTML report so the report can
            be opened independently.
        ============================================================
        */

        stage('Run Smoke Tests') {

            steps {

                echo '=========================================='
                echo '        RUNNING SMOKE TESTS'
                echo '=========================================='


                bat '''
                    python -m pytest ^
                    -m smoke ^
                    -v ^
                    --html=reports/smoke-report.html ^
                    --self-contained-html
                '''

            }
        }


        /*
        ============================================================
        STAGE 6 - RUN REGRESSION TESTS
        ============================================================

        Runs tests marked with:

            @pytest.mark.regression

        Example:

            @pytest.mark.regression
            def test_tc07_invalid_login():
                ...

        The complete regression report will be saved as:

            reports/regression-report.html
        ============================================================
        */

        stage('Run Regression Tests') {

            steps {

                echo '=========================================='
                echo '        RUNNING REGRESSION TESTS'
                echo '=========================================='


                bat '''
                    python -m pytest ^
                    -m regression ^
                    -v ^
                    --html=reports/regression-report.html ^
                    --self-contained-html
                '''

            }
        }

    }


    /*
    ================================================================
    POST ACTIONS
    ================================================================

    The `post` section executes after the pipeline stages finish.

    `always`
        Runs whether tests pass or fail.

    `success`
        Runs only when the pipeline succeeds.

    `failure`
        Runs only when something fails.

    `cleanup`
        Runs at the end for cleanup.
    ================================================================
    */

    post {


        /*
        ============================================================
        ALWAYS
        ============================================================

        This section runs regardless of test result.

        We publish:
            - Smoke report
            - Regression report

        We also archive screenshots.
        ============================================================
        */

        always {

            echo '=========================================='
            echo '        PUBLISHING TEST REPORTS'
            echo '=========================================='


            /*
            --------------------------------------------------------
            Publish pytest HTML reports.

            Jenkins requires the HTML Publisher Plugin for this.

            Jenkins menu:

                Manage Jenkins
                    ↓
                Plugins
                    ↓
                Available Plugins
                    ↓
                HTML Publisher
            --------------------------------------------------------
            */

            publishHTML([

                /*
                Don't fail the entire Jenkins build if the report
                doesn't exist.
                */

                allowMissing: true,


                /*
                Always create a link to the latest report.
                */

                alwaysLinkToLastBuild: true,


                /*
                Keep reports from previous Jenkins builds.
                */

                keepAll: true,


                /*
                Directory containing HTML reports.
                */

                reportDir: 'reports',


                /*
                HTML files generated by pytest-html.

                */

                reportFiles:
                    'smoke-report.html,regression-report.html',


                /*
                Name shown inside Jenkins.
                */

                reportName:
                    'Selenium Pytest Automation Reports',


                /*
                Browser/page title.
                */

                reportTitles:
                    'Smoke Tests, Regression Tests'
            ])


            /*
            --------------------------------------------------------
            Archive screenshots.

            Your Selenium tests can save screenshots like:

                screenshots/TC-SB10-P-label-results.png

            Jenkins stores these as build artifacts.
            --------------------------------------------------------
            */

            archiveArtifacts(

                artifacts:
                    'screenshots/**/*.png',

                /*
                Don't fail the Jenkins build if there are no
                screenshots.
                */

                allowEmptyArchive: true

            )

        }


        /*
        ============================================================
        SUCCESS
        ============================================================

        Runs when all required stages pass.
        ============================================================
        */

        success {

            echo ''
            echo '=========================================='
            echo '       ✅ AUTOMATION PASSED'
            echo '=========================================='
            echo '       Selenium + Pytest'
            echo '       Smoke + Regression'
            echo '=========================================='
            echo ''

        }


        /*
        ============================================================
        FAILURE
        ============================================================

        Runs if any test/stage fails.

        Jenkins build will be marked RED.
        ============================================================
        */

        failure {

            echo ''
            echo '=========================================='
            echo '       ❌ AUTOMATION FAILED'
            echo '=========================================='
            echo '       Check the following:'
            echo ''
            echo '       1. Console Output'
            echo '       2. Pytest HTML Report'
            echo '       3. Screenshots'
            echo '=========================================='
            echo ''

        }


        /*
        ============================================================
        CLEANUP
        ============================================================

        Cleanup processes that might have been left running.

        On Windows Jenkins machines, ChromeDriver can sometimes
        remain running after a failed Selenium test.

        `2>nul` hides the error if chromedriver isn't running.

        `|| exit 0` prevents cleanup failure from failing the
        Jenkins build.
        ============================================================
        */

        cleanup {

            echo '=========================================='
            echo '       CLEANUP'
            echo '=========================================='


            bat '''
                taskkill /F /IM chromedriver.exe /T 2>nul || exit 0
            '''

        }

    }

}
