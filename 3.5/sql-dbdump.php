<?php
/*
*  sql-test.php - Development code for Mycodo SQL database use
*
*  Copyright (C) 2015  Kyle T. Gabriel
*
*  This file is part of Mycodo
*
*  Mycodo is free software: you can redistribute it and/or modify
*  it under the terms of the GNU General Public License as published by
*  the Free Software Foundation, either version 3 of the License, or
*  (at your option) any later version.
*
*  Mycodo is distributed in the hope that it will be useful,
*  but WITHOUT ANY WARRANTY; without even the implied warranty of
*  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
*  GNU General Public License for more details.
*
*  You should have received a copy of the GNU General Public License
*  along with Mycodo. If not, see <http://www.gnu.org/licenses/>.
*
*  Contact at kylegabriel.com
*/

$sqlite_db = "/var/www/mycodo/config/mycodo.sqlite3";

$db = new SQLite3($sqlite_db);

print "Table: Configuration<br>";
$results = $db->query('SELECT row, column FROM Configuration');
while ($row = $results->fetchArray()) {
    print $row[0] . " = " . $row[1] . "<br>";
}

print "<br>Table: PID<br>";
$results = $db->query('SELECT row, column FROM PID');
while ($row = $results->fetchArray()) {
    print $row[0] . " = " . number_format($row[1],1) . "<br>";
}
?>