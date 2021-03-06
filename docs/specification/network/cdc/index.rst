.. _cdc:

Channel Data Classifier
=======================

+-------+--------------------+-------+-----------------------------------------+
| Channel (2 bits)           | Data Classifier (6 bits)                        |
+-------+--------------------+-------+-----------------------------------------+
| ID    | Name               | ID    | Name                                    |
+=======+====================+=======+=========================================+
| 0x0   | :ref:`cdc_urg`     | 0x00  | :ref:`cdc_urg_0x00`                     |
+       +                    +-------+-----------------------------------------+
|       |                    | 0x0A  | :ref:`cdc_urg_0x0A`                     |
+-------+--------------------+-------+-----------------------------------------+
| 0x1   | :ref:`cdc_ed`      |       |                                         |
+-------+--------------------+-------+-----------------------------------------+
| 0x2   | :ref:`cdc_bdcreq`  | 0x09  | :ref:`cdc_bdcreq_0x09`                  |
+       +                    +-------+-----------------------------------------+
|       |                    | 0x0A  | :ref:`cdc_bdcreq_0x0A`                  |
+       +                    +-------+-----------------------------------------+
|       |                    | 0x0B  | :ref:`cdc_bdcreq_0x0B`                  |
+       +                    +-------+-----------------------------------------+
|       |                    | 0x0C  | :ref:`cdc_bdcreq_0x0C`                  |
+       +                    +-------+-----------------------------------------+
|       |                    | 0x0D  | :ref:`cdc_bdcreq_0x0D`                  |
+       +                    +-------+-----------------------------------------+
|       |                    | 0x0E  | :ref:`cdc_bdcreq_0x0E`                  |
+-------+--------------------+-------+-----------------------------------------+
| 0x3   | :ref:`cdc_bdcres`  | 0x09  | :ref:`cdc_bdcres_0x09`                  |
+       +                    +-------+-----------------------------------------+
|       |                    | 0x0A  | :ref:`cdc_bdcres_0x0A`                  |
+       +                    +-------+-----------------------------------------+
|       |                    | 0x0B  | :ref:`cdc_bdcres_0x0B`                  |
+       +                    +-------+-----------------------------------------+
|       |                    | 0x0C  | :ref:`cdc_bdcres_0x0C`                  |
+       +                    +-------+-----------------------------------------+
|       |                    | 0x0D  | :ref:`cdc_bdcres_0x0D`                  |
+       +                    +-------+-----------------------------------------+
|       |                    | 0x0E  | :ref:`cdc_bdcres_0x0E`                  |
+-------+--------------------+-------+-----------------------------------------+


.. toctree::
    :maxdepth: 2

    urg
    ed
    bdcreq
    bdcres
